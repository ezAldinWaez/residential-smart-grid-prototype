Dashboard
=========

Introduction
------------
The dashboard provides the human-machine interface for the residential smart grid prototype. It presents live demand, generation, storage, connection, and virtual battery information through a browser. It also provides controls for simulation execution, house lines, and individual device instances.

Web Application Architecture
----------------------------
The dashboard uses a three-layer architecture. A standards-based browser client provides the user interface. A Starlette application serves the static interface and a small JavaScript Object Notation control application programming interface. Short-lived Pyro5 proxies connect each request to the distributed simulation services.

.. mermaid:: ../_static/diagrams/C6_component_layout.mmd
   :align: center
   :caption: Web dashboard component layout

The web server binds to ``127.0.0.1:8080`` by default. This loopback default prevents other hosts from operating the simulation unless the operator explicitly changes ``RSGP_DASHBOARD_HOST``. The remote object host and port remain configurable through ``RSGP_REMOTE_OBJECT_HOST`` and ``RSGP_REMOTE_OBJECT_PORT``.

The dashboard starts with the following command:

.. code-block:: console

   python -m dashboard

The operator then opens ``http://127.0.0.1:8080`` in a browser.

Interface Structure
-------------------
The interface is an Arabic, right-to-left operational workspace rather than a collection of report pages. Information is ordered by operator intent: system assessment, live power flow, exceptions, residential controls, and engineering evidence. The operator does not need to choose between house, solar, and allocation destinations before understanding a condition.

The application uses a compact, light-only visual theme and occupies the available browser viewport without document scrolling. The power-flow workspace, decision queue, residence list, and dialogs own their overflow independently so controls and headings remain visible.

Operational Assessment
~~~~~~~~~~~~~~~~~~~~~~
The first layer states whether intervention is required and explains the current condition in plain language. A compact signal strip presents residential demand, solar production, physical reserve, and utility exchange. The decision queue groups actionable conditions such as isolated homes, disabled loads, low reserve, and paused services.

The energy-flow panel states the direction and magnitude of battery and utility exchange. A streaming demand trace retains the most recent sixty one-second samples and provides a text summary for assistive technology. Service availability remains visible alongside the decision queue.

Community Operations
~~~~~~~~~~~~~~~~~~~~
Homes form the primary working list. Each stable row shows live demand, demand share, utility connection state, and load-line state. The operator can search the community or filter it to residences that need attention. Native buttons expose their pressed state and provide immediate feedback while a control request is active.

Device controls use the browser ``dialog`` element. The dialog traps focus while open, supports the Escape key, restores focus to the invoking control, and keeps a visible close action. Device configuration text remains collapsed until the operator requests it.

Community-wide utility and load actions use a separate task dialog. This keeps high-impact controls available without allowing them to compete with routine per-house actions.

Engineering Evidence
~~~~~~~~~~~~~~~~~~~~
Solar configuration, physical battery limits, and virtual-reserve allocation are contextual evidence rather than top-level destinations. A dedicated engineering dialog presents these details without expanding the operational canvas. The allocation table keeps rows in house order during updates so content does not shift under keyboard or pointer focus.

Control Application Programming Interface
-----------------------------------------
The Starlette service exposes narrowly scoped routes for the browser client:

- ``GET /api/snapshot`` returns a combined telemetry snapshot.
- ``POST /api/simulation/{action}`` pauses, resumes, or toggles the simulation.
- ``POST /api/houses/lines/{line}`` updates one line type for all houses.
- ``POST /api/houses/{house_idx}/lines/{line}/toggle`` toggles one house line.
- ``GET /api/houses/{house_idx}/devices`` returns one house device snapshot.
- ``POST /api/houses/{house_idx}/devices/{device_name}/{envelope_idx}/toggle`` toggles one device instance.

The browser never receives a generic remote-object interface. This boundary limits the exposed control surface and keeps serialization rules explicit.

Real-Time Update Architecture
-----------------------------
The browser requests a combined snapshot once per second. It stops background polling when the document is hidden and resumes when the document becomes visible. The server creates short-lived Pyro5 proxies for each operation and executes blocking remote calls outside the asynchronous event loop.

The interface keeps stable document elements and updates their text and accessibility states in place. This approach avoids unnecessary layout changes and preserves keyboard focus. A persistent connection banner explains remote service failures and the browser retries automatically.

Accessibility and Responsive Behavior
-------------------------------------
The dashboard uses semantic headings, native buttons, a labeled table, a skip link, visible focus indicators, and text labels for every functional color state. All main controls provide at least a forty-four-pixel interaction target. The demand chart includes a programmatic text summary, while engineering data provides exact values.

Responsive layouts preserve the same content and task order on small phones, tablets, desktop monitors, and landscape orientation. There is no separate mobile navigation model. At compact sizes the same panels reflow while retaining their own scrolling regions. Reduced-motion preferences disable nonessential control transitions. The light theme is enforced independently of the operating-system color preference.
