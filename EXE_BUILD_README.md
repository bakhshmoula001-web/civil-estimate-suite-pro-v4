# Civil Estimate Suite Pro v4.0 — Final EXE Build

Before building, confirm these source files have been replaced:

- config\setting.py
- app\application_context.py

Then run:

1. clean_build.bat
2. build_exe.bat

Expected output:

dist\
└── Civil Estimate Suite Pro 4.0\
    ├── Civil Estimate Suite Pro 4.0.exe
    └── _internal\
        ├── config\
        └── database\

The EXE should be tested from its complete ONEDIR folder.
Do not move the EXE out of that folder.

Writable user data is handled by the production-safe source files:
%LOCALAPPDATA%\Civil Estimate Suite Pro\
