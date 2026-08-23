# OpenFOAM MCP — Install & Usage Guide

This guide covers two situations:

1. **Testing it yourself now** — before you've published to PyPI (install from
   the wheel file you already have).
2. **What your buyers will do** — after you publish to PyPI (`uvx openfoam-mcp`).

Windows is shown first (your setup); macOS/Linux notes follow.

---

## 1. Prerequisites

- **Python 3.10 or newer.** Check with `python --version` in a terminal
  (PowerShell or Command Prompt). If missing, install from python.org and tick
  *"Add Python to PATH"* during setup.
- **Claude Desktop** installed.
- (Optional, for buyers) **uv** — the fast Python runner that provides `uvx`.
  Install on Windows with:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

You do **not** need OpenFOAM installed. Most tools are pure Python; the few that
call OpenFOAM utilities simply say so when it isn't present.

---

## 2A. Install it yourself (from the wheel) — Windows

You have `openfoam_mcp-0.1.0-py3-none-any.whl`. Open PowerShell and run:

```powershell
pip install "C:\path\to\openfoam_mcp-0.1.0-py3-none-any.whl"
```

That installs the server plus its dependency (the `mcp` SDK). Verify it runs:

```powershell
python -m openfoam_mcp
```

It will sit silently waiting for input (that's correct — it's an MCP server that
talks over stdin/stdout). Press `Ctrl+C` to stop. If you see no import error,
it's working.

## 2B. Install it yourself (from source) — any OS

From inside the unzipped project folder:

```bash
pip install -e ".[dev]"
pytest          # optional: runs the 16-test suite
python -m openfoam_mcp
```

---

## 3. Connect it to Claude Desktop

Open the config file (create it if it doesn't exist):

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
  (paste that into the File Explorer address bar)
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add an `openfoam` entry under `mcpServers`.

### Option 1 — using the wheel/pip install (recommended for you now)

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "python",
      "args": ["-m", "openfoam_mcp"]
    }
  }
}
```

> If `python` isn't found by Claude Desktop, use the full path instead, e.g.
> `"command": "C:\\Users\\<you>\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"`.
> Find it by running `where python` (Windows) or `which python3` (macOS/Linux).

### Option 2 — using uvx (what buyers use once it's on PyPI)

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "uvx",
      "args": ["openfoam-mcp"]
    }
  }
}
```

To test the uvx path **before** publishing, point it at your local wheel:

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "uvx",
      "args": ["--from", "C:\\path\\to\\openfoam_mcp-0.1.0-py3-none-any.whl", "openfoam-mcp"]
    }
  }
}
```

**Save the file, then fully quit and reopen Claude Desktop** (use the tray icon →
Quit, not just closing the window).

---

## 4. Verify it loaded

In Claude Desktop, click the tools/plug icon in the message box. You should see
**openfoam** listed with 13 tools. If it's not there, see Troubleshooting below.

---

## 5. How to use it

You talk to it in plain English — Claude decides which tool to call. You don't
type tool names. Below are the tools grouped by what you'd ask for, with example
prompts.

### The easy way — let it plan and mesh for you

- **Start from intent** (it asks for anything it needs):
  *"I want to simulate flow through a 50 mm water pipe at 2 m/s — set it up."*
  It replies with the recommended solver, turbulence model, target y+, mesh
  preset, boundary conditions and a step-by-step plan. If you leave out the
  velocity or size, it asks you for just that.
- **Auto-generate the mesh** (no hand-writing vertices):
  *"Generate a graded channel blockMesh in C:\cfd\pipe with a first-cell height
  of 0.02 mm."* It writes a valid `system/blockMeshDict` with wall grading
  computed for you.

A full hands-off flow looks like: *"Air at 25 m/s over a 1 m plate — plan it,
auto-mesh it, and scaffold the case in ./plate."* → it plans → generates the
graded blockMesh → scaffolds the case → checks it. You then run `blockMesh` and
the solver.

**Which OpenFOAM do you run?** By default cases use the classic style
(`application simpleFoam;`), which works on ESI OpenFOAM and Foundation v10 and
earlier. If you're on **OpenFOAM Foundation v11 or v12**, ask for the v12 style:
*"Scaffold it for OpenFOAM v12."* — the case then uses `application foamRun;` and
you run `foamRun` instead of `simpleFoam`.

### Sizing the flow and mesh (no files needed)

- **Reynolds number & turbulence model**
  *"I have water at 2 m/s through a 50 mm pipe. What Reynolds number is that and
  which turbulence model should I use?"*
- **First-cell height for a target y+**
  *"Air at 30 m/s over a 0.5 m flat plate — what first-cell height do I need for
  y+ = 1? And for wall functions at y+ = 50?"*
- **Check a y+ you already have**
  *"My first cell is 0.02 mm tall at 30 m/s over 0.5 m. What y+ will that give?"*
- **Inlet turbulence values**
  *"Give me inlet k, omega and nut for 10 m/s, 5% turbulence intensity, 14 mm
  length scale."*
- **Transient time step**
  *"For 10 m/s and 1 mm cells, what time step keeps Courant number at 1?"*

### Building a case

- **Scaffold a case**
  *"Scaffold a steady simpleFoam case in C:\cfd\duct at 12 m/s and check it."*
  Claude writes `system/`, `constant/`, and `0/` with a box mesh (patches:
  inlet, outlet, walls, frontAndBack), then validates it.
- **List available templates**
  *"What solver templates can you scaffold?"* → simpleFoam (steady RANS),
  pimpleFoam (transient RANS), icoFoam (transient laminar).

### Editing an existing case

- **Read a dictionary**
  *"Show me system/controlDict in C:\cfd\duct."*
- **Change a setting**
  *"Set endTime to 3000 in C:\cfd\duct\system\controlDict."*
- **Change a boundary condition**
  *"In C:\cfd\duct\0\U, set the inlet to fixedValue (15 0 0)."*

### Checking and debugging

- **Validate a case**
  *"Check the case in C:\cfd\duct — are the patches and turbulence fields
  consistent?"* Reports missing files, patch mismatches between mesh and fields,
  and turbulence fields that don't match the model.
- **Read a residual log**
  *"Read C:\cfd\duct\log.simpleFoam and tell me if it converged."* Returns a
  verdict (converged / diverging / NaN / still running) with how many orders of
  magnitude each field's residual dropped.
- **Run an OpenFOAM utility** (only if OpenFOAM is installed)
  *"Run checkMesh in C:\cfd\duct."* Whitelisted to safe utilities (blockMesh,
  checkMesh, foamDictionary, renumberMesh, decomposePar, foamListTimes,
  surfaceCheck, transformPoints).

### A full worked walkthrough

> **You:** *"I'm simulating air at 25 m/s over a 1 m plate. What Reynolds number
> is that, what y+=1 first-cell height do I need, then scaffold a simpleFoam
> case in ./plate at that velocity and check it."*
>
> Claude will: compute Re ≈ 1.7×10⁶ (turbulent, recommend k-ω SST) → compute the
> first-cell height → call `scaffold_case` to write the case → call `check_case`
> and report it passed. You then run `blockMesh` and `simpleFoam` yourself, and
> come back with *"read ./plate/log.simpleFoam"* to check convergence.

---

## 6. Notes on file paths

The scaffolding, dictionary, check, and residual tools read and write files on
the machine where the server runs. On Claude Desktop that's your own computer, so
use real local paths (e.g. `C:\cfd\duct`). Use paths you have permission to write
to. The `run_openfoam_command` tool only runs a fixed whitelist of read/setup
utilities — it will refuse anything else.

---

## 7. Troubleshooting

- **Tools don't appear:** confirm the JSON is valid (no trailing commas), you
  fully quit and reopened Claude Desktop, and `command` points to a Python that
  has the package. Test in a terminal first with `python -m openfoam_mcp`.
- **"No module named openfoam_mcp":** Claude Desktop is using a different Python
  than the one you pip-installed into. Put the full path to that Python in
  `command`, or install with that Python's `pip`.
- **"No module named mcp.server.fastmcp":** you have `mcp` 2.0+. Reinstall the
  1.x line: `pip install "mcp>=1.2.0,<2.0.0"`. (The package already pins this,
  so a clean install avoids it.)
- **A tool says OpenFOAM isn't found:** that's expected without OpenFOAM — only
  `run_openfoam_command` and nested-key dictionary edits need it. Everything else
  works regardless.
- **See what's happening:** Claude Desktop logs MCP output under
  `%APPDATA%\Claude\logs\` (Windows) — check `mcp-server-openfoam.log`.

---

## 8. Uninstall

```bash
pip uninstall openfoam-mcp
```

Then remove the `openfoam` block from `claude_desktop_config.json`.
