# LaTeX Documentation

This folder contains the academic report in LaTeX format.

## Files

- `MemoryES.tex` — Original Spanish report (source)
- `MemoryEN.tex` — English translation (source, optional)
- `*.bib` — Bibliography files
- `figures/` — External figures referenced by LaTeX

## Compilation

Compile with:

```bash
pdflatex MemoryES.tex
bibtex MemoryES
pdflatex MemoryES.tex
pdflatex MemoryES.tex
```

Or using `latexmk` (recommended):

```bash
latexmk -pdf -bibtex MemoryES.tex
```

## Output

The compiled PDF will be saved in the repository root as `MemoryES.pdf` or `MemoryEN.pdf`.

---

**Note:** All LaTeX sources from the `Proyecto/REDACCION/` directory should be copied here for compilation.
