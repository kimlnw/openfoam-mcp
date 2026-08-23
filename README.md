# OpenFOAM MCP by iLab — a CFD co-pilot for any MCP client

`openfoam-mcp` is a [Model Context Protocol](https://modelcontextprotocol.io)
server that turns an AI assistant (Claude Desktop, and any other MCP client)
into an OpenFOAM setup and debugging co-pilot. It scaffolds runnable cases,
edits dictionaries safely, sizes your near-wall mesh, computes inlet turbulence
values, and reads solver logs to tell you whether a run converged or blew up —
all without you leaving the chat.

Most of the tools are **pure Python and need no OpenFOAM installation**, so they
work anywhere. The few that call OpenFOAM utilities (e.g. `blockMesh`,
`checkMesh`) detect the environment and degrade gracefully when it is absent.

> **Validated end-to-end on real OpenFOAM (ESI v1912).** Generated cases run
> through `blockMesh` and the solvers — simpleFoam converges, all four mesh
> presets produce valid meshes, and the real logs are read back correctly by the
> residual and mesh-quality parsers. See [`VALIDATION.md`](VALIDATION.md).

### OpenFOAM version support

`scaffold_case` takes an `openfoam_flavor`:

- `classic` (default) — `application <solver>;` with `transportProperties`.
  Validated on ESI v1912; works on ESI v2006+ and Foundation v8–v10.
- `foundation-v12` — `application foamRun;` + `solver incompressibleFluid;` with
  `physicalProperties`, for OpenFOAM **Foundation v11/v12**. Run `foamRun` instead
  of the solver name.

## Why it's useful

Setting up a CFD case is fiddly bookkeeping: the right `y+`, matching boundary
patches between the mesh and every `0/` field, consistent turbulence fields for
the chosen model, a stable Courant number, and reading pages of residual output
to see if it converged. This server does that bookkeeping through natural
language.

## Make the hard part simple

Two tools do the work most people find fiddly:

- **`recommend_setup`** — tell it your goal in plain words ("flow through a
  pipe", "drag on a car") and it returns the solver, turbulence model, target
  `y+`, mesh preset, per-patch boundary conditions and a numbered plan — asking
  you for only the numbers it still needs.
- **`generate_blockmesh`** — auto-writes a valid, boundary-layer-**graded**
  `blockMeshDict` from a geometry preset. Give it your target first-cell height
  and it computes the wall grading for you. No hand-writing vertices or blocks.

## Tools (20)

| Tool | What it does |
|------|--------------|
| `recommend_setup` | **Start here.** Goal to solver, model, mesh preset, BCs, plan (asks for missing inputs). |
| `generate_blockmesh` | **Auto blockMesh** with wall grading auto-sized to your y+ (presets: channel, flatplate, step, box). |
| `list_mesh_presets` | List the blockMesh geometry presets. |
| `list_solvers` | List scaffold-able solver templates (simpleFoam, pimpleFoam, icoFoam). |
| `flow_regime` | Reynolds number, laminar/turbulent verdict, turbulence-model recommendation. |
| `first_cell_height` | First-cell height for a target `y+` (flat-plate correlation). |
| `y_plus_from_height` | Inverse: predicted `y+` from a cell height, with regime warning. |
| `inlet_turbulence` | Inlet `k`, `epsilon`, `omega`, `nut` from intensity + length scale. |
| `time_step_from_cfl` | Transient time step from a target Courant number. |
| `pipe_pressure_drop` | Colebrook-White friction factor + Darcy-Weisbach pressure drop / head loss. |
| `heat_transfer_pipe` | Convective `h` for internal flow (Dittus-Boelter Nusselt). |
| `scaffold_case` | Write a runnable case tree (`system/`, `constant/`, `0/`) for a solver. |
| `read_dict` | Read a dictionary file or a single entry (via `foamDictionary`). |
| `set_dict_entry` | Set a dictionary keyword (nested via `foamDictionary`; text fallback). |
| `set_boundary_condition` | Set/insert a patch's `boundaryField` entry in a `0/` field. |
| `analyze_stl` | STL watertight/manifold check, bbox, area, volume, snappyHexMesh prep. |
| `mesh_quality_report` | Parse a `checkMesh` log into a non-ortho/skewness/aspect verdict + scheme advice. |
| `check_case` | Validate a case: files present, turbulence fields consistent, patches match mesh. |
| `analyze_residuals` | Parse a solver log into per-field residual drop + convergence verdict. |
| `run_openfoam_command` | Run a whitelisted OpenFOAM utility inside a case (if installed). |

See [`COMPARISON.md`](COMPARISON.md) for how this stacks up against the other
OpenFOAM MCP server.

## Install & run

The server ships as a PyPI package with a console entry point, so the usual
zero-install runner is [`uvx`](https://docs.astral.sh/uv/):

```bash
uvx openfoam-mcp
```

or install it into an environment:

```bash
pip install openfoam-mcp
openfoam-mcp
```

### Claude Desktop configuration

Add this to `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/`,
Windows: `%APPDATA%\Claude\`):

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

Restart Claude Desktop; the OpenFOAM tools appear under the tools menu.

## Example prompts

- "I have air at 30 m/s over a 0.5 m chord. What Reynolds number is that, and
  what first-cell height do I need for y+ = 1?"
- "Scaffold a steady simpleFoam case in ./duct at 12 m/s and check it."
- "Set `endTime` to 3000 in ./duct/system/controlDict."
- "Read ./duct/log.simpleFoam and tell me if it converged."

## Solver templates

| Template | Physics | Typical use |
|----------|---------|-------------|
| `simpleFoam` | Steady incompressible RANS (k-ω SST) | Ducts, external aero, general steady flow |
| `pimpleFoam` | Transient incompressible RANS (k-ω SST) | Vortex shedding, unsteady flows |
| `icoFoam` | Transient incompressible laminar | Low-Re teaching cases (cavity, low-Re pipe) |

Templates follow the OpenFOAM foundation v9–v12 / ESI v2306+ tutorial style
(`transportProperties` + `momentumTransport`). The generated box mesh has
patches `inlet`, `outlet`, `walls`, `frontAndBack`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT © 2026 iLab (Tanawat Manokieng)
