## Backend Archive

This folder stores backend files that were removed from active runtime paths during
organization cleanup, but retained for traceability and recovery.

- `legacy_routers/`: duplicate or non-canonical router modules that were not mounted.
- `legacy_root/`: historical test scripts, reports, and helper scripts moved out of
  backend root to keep the runtime surface clean.

Nothing in this folder is imported by the backend application entrypoint.
