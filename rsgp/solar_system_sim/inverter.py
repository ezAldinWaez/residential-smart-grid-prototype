"""Solar system simulated inverter using PVLib."""

import pvlib


class Inverter:
    """
    Solar system simulated inverter.
    Uses the pvlib.inverter.pvwatts model: pvwatts(pdc, pdc0, eta_inv_nom, eta_inv_ref).
    """
    Paco: float  #: Nameplate AC power rating of the inverter (W). Used to cap output.
    #: DC power rating of the inverter (W). This is pdc0 for pvwatts.
    Pdco: float
    eta_inv_nom: float  #: Nominal inverter efficiency (e.g., 0.96).
    eta_inv_ref: float  #: Reference inverter efficiency (e.g., 0.9637).
    Pnt: float  #: AC power consumed by the inverter at night (W).

    # Simplified overall efficiency for reverse calculation (DC for AC load)
    # This can be eta_inv_nom or Paco / Pdco, or a specific value from settings.
    effective_nominal_efficiency: float
    #: Flag indicating if the inverter is connected to the utility grid.
    is_grid_connected: bool

    def __init__(
        self,
        paco: float,
        pdco: float,
        eta_inv_nom: float,
        eta_inv_ref: float,
        pnt: float,
        effective_nominal_efficiency: float,  # For the reverse calculation
        initial_grid_status: bool = True,
    ):
        self.Paco = paco
        self.Pdco = pdco  # This is pdc0 for the pvwatts function
        self.eta_inv_nom = eta_inv_nom
        self.eta_inv_ref = eta_inv_ref
        self.Pnt = pnt  # For night consumption, not part of this pvwatts model directly
        self.effective_nominal_efficiency = effective_nominal_efficiency
        self.is_grid_connected = initial_grid_status

    def set_grid_status(self, is_connected: bool):
        """Allows external control over the grid connection status."""
        self.is_grid_connected = is_connected

    def get_ac_output(self, p_dc: float) -> float:
        """
        Calculates the AC power produced from a given DC input power.
        Args:
            p_dc (float): DC power available to the inverter (W).
        Returns:
            float: AC power produced (W), capped at self.Paco.
        """
        if p_dc <= 0:
            return 0.0

        # Call pvlib.inverter.pvwatts with the specified signature
        # Defaults for eta_inv_nom and eta_inv_ref are 0.96 and 0.9637 respectively in pvlib,
        # but we are using the values passed during __init__.
        ac_power_calculated = pvlib.inverter.pvwatts(
            pdc=p_dc,
            pdc0=self.Pdco,
            eta_inv_nom=self.eta_inv_nom,
            eta_inv_ref=self.eta_inv_ref
        )

        # The pvwatts model calculates efficiency and then AC power.
        # It's important to ensure the output does not exceed the inverter's AC nameplate rating (Paco).
        actual_ac_power = min(float(ac_power_calculated), self.Paco)

        return max(0.0, actual_ac_power)

    def get_dc_input_for_ac_output(self, p_ac_target: float) -> float:
        """
        Calculates the DC power required to produce a target AC output power.
        Uses the simplified effective_nominal_efficiency for this reverse calculation.
        Args:
            p_ac_target (float): Target AC output power (W).
        Returns:
            float: Required DC input power (W).
        """
        if p_ac_target <= 0:
            return 0.0
        # Ensure target AC does not exceed inverter's capability
        p_ac_target_capped = min(p_ac_target, self.Paco)

        if self.effective_nominal_efficiency == 0:  # Avoid division by zero
            return float('inf')

        p_dc_required = p_ac_target_capped / self.effective_nominal_efficiency
        return p_dc_required

    def get_night_consumption(self) -> float:
        """Returns the AC power consumed by the inverter at night (W)."""
        return self.Pnt

    def __str__(self):
        return (
            f"Inverter Status: Paco={self.Paco}W, Pdco={self.Pdco}W, Grid Connected: {self.is_grid_connected}, "
            f"Night Consumption: {self.Pnt}W, Nom. Eff: {self.eta_inv_nom*100:.2f}%"
        )
