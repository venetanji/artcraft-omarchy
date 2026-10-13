import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "artcraft"


class LauncherTests(unittest.TestCase):
  def run_launcher(self, arguments=(), overrides=None, exit_code=0):
    with tempfile.TemporaryDirectory() as directory:
      binary = Path(directory) / "fake-artcraft"
      binary.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "print(json.dumps({'arguments': sys.argv[1:], "
        "'dmabuf': os.environ.get('WEBKIT_DISABLE_DMABUF_RENDERER'), "
        "'compositing': os.environ.get('WEBKIT_DISABLE_COMPOSITING_MODE')}))\n"
        f"sys.exit({exit_code})\n"
      )
      binary.chmod(0o755)
      environment = os.environ.copy()
      environment.pop("WEBKIT_DISABLE_DMABUF_RENDERER", None)
      environment.pop("WEBKIT_DISABLE_COMPOSITING_MODE", None)
      environment.update(overrides or {})
      environment["ARTCRAFT_BINARY"] = str(binary)
      return subprocess.run(
        ["bash", str(LAUNCHER), *arguments], env=environment,
        text=True, capture_output=True, check=False,
      )

  def test_wayland_workaround_and_argument_forwarding(self):
    result = self.run_launcher(["a path with spaces", "--example"])
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(json.loads(result.stdout), {
      "arguments": ["a path with spaces", "--example"],
      "dmabuf": "1", "compositing": None,
    })

  def test_preserves_explicit_renderer_preferences(self):
    result = self.run_launcher(overrides={
      "WEBKIT_DISABLE_DMABUF_RENDERER": "0",
      "WEBKIT_DISABLE_COMPOSITING_MODE": "1",
    })
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(json.loads(result.stdout)["dmabuf"], "0")
    self.assertEqual(json.loads(result.stdout)["compositing"], "1")

  def test_propagates_application_failure(self):
    self.assertEqual(self.run_launcher(exit_code=42).returncode, 42)

  def test_help_does_not_launch_the_application(self):
    result = self.run_launcher(["--help"], exit_code=42)
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn("--diagnose", result.stdout)


if __name__ == "__main__":
  unittest.main()
