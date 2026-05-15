# Jupyter Dataloader — seed application data

Before accessing the DIGIT STUDIO UI for the first time, you must seed the master data using the **Dataloader** Jupyter notebook. Do this **after `tilt up` has finished** and all services are healthy.

---

## Steps

### 1. Open the Tilt UI

Navigate to **http://localhost:10350/** in your browser.

---

### 2. Locate the Jupyter pod

In the Tilt UI, go to the **Tools** section in the resource list and click on the **jupyter** resource.

---

### 3. Open JupyterLab

With the jupyter resource selected, click the **"via lab"** tab/link. This opens **JupyterLab** in a new browser tab.

---

### 4. Open the Dataloader notebook

In the JupyterLab file browser on the left, click **`Dataloader.ipynb`**. The notebook opens in the main area showing a sequence of cells.

There are two types of cells:

| Type | Description |
|------|-------------|
| **Markdown cell** | Formatted text — explains what the next step does. Not executable. |
| **Executable cell** | Code that runs against the stack. Must be run in order. |

---

### 5. Execute cells in sequence

Run each cell **top to bottom, one at a time**, using:

```
Shift + Enter
```

**Do not skip cells or run them out of order.**

#### Credentials (used in the second executable cell)

When prompted for login credentials during execution, enter:

| Field | Value |
|-------|-------|
| **Username** | `ADMIN` |
| **Password** | `eGov@123` |

Wait for each cell to finish (the `[*]` indicator on the left changes to a number, e.g. `[1]`) before running the next one.

---

### 6. Access the application

Once all cells have executed successfully, the data is seeded. Open the DIGIT UI:

**http://localhost:18000/digit-studion/employee/login**

---

## Related

- **[QUICK-SETUP.md](../QUICK-SETUP.md)** — `tilt up`, access URLs, stopping the stack
- **[docs/TILT.md](TILT.md)** — Tilt CLI install and troubleshooting
