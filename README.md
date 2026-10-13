# Artcraft on Omarchy

Linux build and launch scripts for the upstream [Artcraft desktop app](https://github.com/storytold/artcraft).
This project builds the Tauri app, including its React frontend, on Omarchy/Arch Linux x86_64.

The release executable was built and launched successfully on Omarchy 4.0.4 with
Rust 1.99.0 and WebKitGTK 2.52.6. The first launch renders the account sign-up/login
screen. Arch package and automated release work will follow desktop evaluation.

The build is pinned to Artcraft 0.42.0, upstream commit
`d4e4ac69bbd93d237eaf5d0260bc6a5ff3a5e373`. It uses the upstream providers and app settings.

## Build and run

Install Rust through [rustup](https://rustup.rs/) and Node.js 22 or newer. On Omarchy,
the system build dependencies are available through:

```sh
omarchy pkg add base-devel clang cmake pkgconf webkit2gtk-4.1 gtk3 libsoup3 openssl librsvg
```

Then run:

```sh
git clone https://github.com/venetanji/artcraft-omarchy.git
cd artcraft-omarchy
./scripts/build
./scripts/run
```

The first build downloads the upstream source, frontend packages, a pinned Tauri CLI,
and Rust dependencies. Build files stay in `.build/`. The frontend is built from its
app directory so Tailwind finds its configuration. Rust uses the checked-in Cargo
lockfile and SQLx offline metadata. No database server is required to build.

Rebuild with `./scripts/build`. Set `ARTCRAFT_FORCE_INSTALL=1` to reinstall frontend
dependencies from their lockfile. `ARTCRAFT_BUILD_ROOT` selects a different build
directory. The executable is `.build/artcraft/target/release/artcraft`.

Artcraft stores its data in `~/Artcraft/`, including settings, downloaded media, task
state and credentials. It connects to its existing online generation providers;
building the desktop app does not run image or video models locally. Launching it
does not submit a generation request.

## Wayland

The launcher sets `WEBKIT_DISABLE_DMABUF_RENDERER=1` by default for WebKitGTK/Wayland
compatibility, preserving an explicit environment override. It leaves compositing
enabled. To try WebKit's default renderer:

```sh
WEBKIT_DISABLE_DMABUF_RENDERER=0 ./scripts/run
```

If the window stays blank, try:

```sh
WEBKIT_DISABLE_COMPOSITING_MODE=1 ./scripts/run
```

That fallback can affect GPU rendering. `./scripts/run --diagnose` prints desktop
session and WebKit package information without opening the app.

## Agent interface findings

At the pinned revision, the desktop executable has no generation CLI or MCP
listener. Its native commands are exposed to its frontend through Tauri IPC.
The repository includes MCP session wire types, which do not start a desktop
agent server. Its prompted 3D scene integration is documented upstream as unfinished.

Artcraft does have a separate API-key generation surface. See the upstream
[Omni API guide](https://github.com/storytold/artcraft/blob/d4e4ac69bbd93d237eaf5d0260bc6a5ff3a5e373/_docs/artcraft_omni_api.md)
and [API reference](https://storyteller-docs.netlify.app/). API access requires an
enabled Artcraft account.

[Easel](https://easel.ait4x.org/docs) is an available independent media backend, and
[easel-client's Media MCP](https://github.com/venetanji/easel-client/tree/main/packages/media-mcp)
already provides its agent interface. This build does not add an Easel provider to
Artcraft or replace its existing backend. Desktop exploration comes first.

## Verification

```sh
python3 -m unittest discover -s tests -v
bash -n scripts/artcraft scripts/build scripts/run
```

Launcher tests check argument forwarding, renderer overrides, process exit codes,
and help without starting the application. A real desktop launch is needed to
verify WebKit rendering on the target machine.

## License

The build scripts in this repository are MIT licensed. Upstream Artcraft is
MIT OR Apache-2.0; its third-party notices and trademark terms remain applicable.
See upstream [NOTICE](https://github.com/storytold/artcraft/blob/d4e4ac69bbd93d237eaf5d0260bc6a5ff3a5e373/NOTICE).
