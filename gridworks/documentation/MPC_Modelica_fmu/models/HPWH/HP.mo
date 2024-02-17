within models.HPWH;
package HP
  model hp_equations
    parameter Modelica.Units.SI.HeatFlowRate Q_heat_nominal;
    Modelica.Blocks.Interfaces.RealInput Tevap
      "Temperature of evaporator side of heat pump (e.g. outside air temperature if ducted)"
      annotation (Placement(transformation(extent={{-140,70},{-100,110}})));
    Modelica.Blocks.Interfaces.RealInput Tbottom
      annotation (Placement(transformation(extent={{-140,30},{-100,70}})));
    Modelica.Blocks.Interfaces.RealOutput PEle "Electrical power consumption"
      annotation (Placement(transformation(extent={{100,80},{120,100}})));
    Modelica.Blocks.Interfaces.RealOutput EEle "Electrical power consumption"
      annotation (Placement(transformation(extent={{100,40},{120,60}})));
    Modelica.Blocks.Interfaces.RealOutput Qheat "Electrical power consumption"
      annotation (Placement(transformation(extent={{100,0},{120,20}})));
    Buildings.Controls.OBC.CDL.Interfaces.BooleanInput u "On/off  signal"
      annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Real Tbottom_degC = Tbottom - 273.15;
      Real Tevap_degC = Tevap - 273.15;
    Modelica.Blocks.Interfaces.RealOutput Eheat "Electrical power consumption"
      annotation (Placement(transformation(extent={{100,-40},{120,-20}})));
      Real Q_heat_nominal_on;
  equation
    Q_heat_nominal_on = if u then Q_heat_nominal else 0;
    Qheat = Q_heat_nominal_on * (1.24534738 + 3.47447494e-04 * Tbottom_degC + 1.13016771e-02 * Tevap_degC -1.04789659e-04 * Tbottom_degC ^ 2 + 1.31015765e-04 * Tevap_degC ^2);
    PEle = Q_heat_nominal_on * (1.94878810e-01 + 1.35139016e-03 * Tbottom_degC -3.76075304e-03 * Tevap_degC ^2 + 3.43039433e-05 * Tbottom_degC ^ 2 + 1.59557400e-04 * Tevap_degC ^2);
    der(EEle) = PEle / 3600 / 1000;
    der(Eheat) = Qheat / 3600 / 1000;

    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)),
      Documentation(info="<html>
<p>Heat pum equations : </p>
<p><br>Qheat = Q_heat_nominal_on * (\\alpha_0 + \\alpha_1 * Tbottom + \\alpha_2 * Tevap + \\alpha_3 * Tbottom ^ 2 + \\alpha_4 * Tevap ^2) </p>
<p><br>PEle = Q_heat_nominal_on * (\\beta_0 + \\beta_1 * Tbottom + \\beta_2 * Tevap ^2 + \\beta_3 * Tbottom^ 2 + \\beta_4 * Tevap ^2)</p>
</html>"));
  end hp_equations;
end HP;
