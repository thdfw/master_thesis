within models.HPWH;
model HPWH_virtual
  "A model for a heat pump domestic water heater with tank and auxiliary electric heater"
extends Buildings.Fluid.Interfaces.PartialTwoPortInterface;
  parameter Modelica.Units.SI.Temperature Tminout= 2.8 + 273.15
    "Temperature setpoint of hot water supply from heater";
      parameter Real Upper_deadband=11.25
    "Upper deadband";
    parameter Real Lower_deadband=13
    "Lower deadband";
  parameter Modelica.Units.SI.Power QHeaPum_flow_nominal
    "Nominal heating capacity of the heat pump"
annotation (Dialog(tab="Heating", group="HP"));
  parameter Modelica.Units.SI.Power Qres_nominal
    "Nominal heating capacity of the resistance"
annotation (Dialog(tab="Heating", group="Resistance"));
  parameter Modelica.Units.SI.Volume VTan "Tank volume";
  parameter Modelica.Units.SI.Length hTan "Height of tank (without insulation)";
  parameter Modelica.Units.SI.Length dIns "Thickness of insulation";
  parameter Modelica.Units.SI.ThermalConductivity kIns=0.04
    "Specific heat conductivity of insulation";
  parameter Modelica.Units.SI.Temperature initial_temperature=51.7 + 273.15;
  Modelica.Blocks.Interfaces.RealInput Tevap(final quantity="ThermodynamicTemperature",
                                          final unit="K",
                                          displayUnit = "degC")
    "Temperature of evaporator side of heat pump (e.g. outside air temperature if ducted)"
    annotation (Placement(transformation(extent={{-140,50},{-100,90}})));
  Buildings.Fluid.Storage.StratifiedEnhanced tan(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal=m_flow_nominal,
    VTan=VTan,
    hTan=hTan,
    dIns=dIns,
    kIns=kIns,
    nSeg=tank_nSeg,
    T_start=initial_temperature)
                  "Hot water tank"
    annotation (Placement(transformation(extent={{10,-10},{-10,10}})));

  Buildings.HeatTransfer.Sources.PrescribedHeatFlow heaFlo_res_top
    annotation (Placement(transformation(extent={{40,60},{60,80}})));
  Buildings.HeatTransfer.Sources.PrescribedHeatFlow heaFlo_hp[nSeg]
    annotation (Placement(transformation(extent={{40,-60},{60,-40}})));
  Modelica.Blocks.Interfaces.RealInput Toutside(final quantity="ThermodynamicTemperature",
                                          final unit="K",
                                          displayUnit = "degC")
    "Temperature of evaporator side of heat pump (e.g. outside air temperature if ducted)"
    annotation (Placement(transformation(extent={{-140,80},{-100,120}})));
  Modelica.Blocks.Interfaces.RealInput Tset_user(
    final quantity="ThermodynamicTemperature",
    final unit="K",
    displayUnit="degC")
    "Temperature of evaporator side of heat pump (e.g. outside air temperature if ducted)"
    annotation (Placement(transformation(extent={{-140,20},{-100,60}})));
  Modelica.Blocks.Math.BooleanToReal booleanToReal(realTrue=Qres_nominal)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-10,70})));
  HP.hp_equations hp_equations(Q_heat_nominal=QHeaPum_flow_nominal)
    annotation (Placement(transformation(extent={{-20,-80},{0,-60}})));
  Modelica.Blocks.Interfaces.RealInput Tambient(final quantity="ThermodynamicTemperature",
                                          final unit="K",
                                          displayUnit = "degC")
    "Temperature of evaporator side of heat pump (e.g. outside air temperature if ducted)"
    annotation (Placement(transformation(extent={{-140,-110},{-100,-70}})));
  Buildings.HeatTransfer.Sources.PrescribedTemperature preTem
    annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
  parameter Modelica.Units.SI.Temperature cut_temperature=5 + 273.15
    "Below this temperature, HP is off"
    annotation (Dialog(tab="Heating", group="HP"));
  parameter Modelica.Units.SI.Time cycle_time=300
    "Cycle time for the HP"
    annotation (Dialog(tab="Heating", group="HP"));
  parameter Modelica.Blocks.Interfaces.RealOutput deadband_hp=0.0
    "Deaband for the HP" annotation (Dialog(tab="Heating", group="HP"));
  parameter Modelica.Blocks.Interfaces.RealOutput deadband_hp_recent=0.0
    "Deaband for the HP (recent Tset change)" annotation (Dialog(tab="Heating", group="HP"));
  parameter Modelica.Blocks.Interfaces.RealOutput deadband_low_stratification
    =5 "Deadband in case of low stratification" annotation (Dialog(tab="Heating", group="HP"));
  parameter Real res_deadband=5 "Deaband for the resistance"
    annotation (Dialog(tab="Heating", group="Resistance"));
  parameter Real res_deadband_hpactive=5
    "Deaband for the resisance (when HP is active)"
    annotation (Dialog(tab="Heating", group="Resistance"));
  parameter Modelica.Units.SI.Time hp_timewindow=0
    "Wait time after T change to switch back to normal deadband"
    annotation (Dialog(tab="Heating", group="HP"));
  Modelica.Blocks.Math.BooleanToReal booleanToReal1(realTrue=Qres_nominal)
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-10,-30})));
  Buildings.HeatTransfer.Sources.PrescribedHeatFlow heaFlo_res_bottom
    annotation (Placement(transformation(extent={{40,-40},{60,-20}})));
  Controls.model_a.summary_state_cta summary_state_cta(
    cut_temperature=cut_temperature,
    cycle_time=cycle_time,
    deadband_hp=deadband_hp,
    deadband_hp_recent=deadband_hp_recent,
    deadband_low_stratification=deadband_low_stratification,
    res_deadband=res_deadband,
    res_deadband_hpactive=res_deadband_hpactive,
    hp_timewindow=hp_timewindow,
    cta_dt_loadup=cta_dt_loadup,
    cta_dt_advanced=cta_dt_advanced,
    cta_dt_shed=cta_dt_shed,
    cta_user_deadband=cta_user_deadband)
    annotation (Placement(transformation(extent={{-60,-80},{-40,-60}})));
  Modelica.Blocks.Interfaces.IntegerInput cta_signal annotation (Placement(
        transformation(
        extent={{-20,-20},{20,20}},
        rotation=270,
        origin={0,120})));
  parameter Modelica.Units.SI.Time cta_dt_loadup=0
    "Wait time before transition fires"
    annotation (Dialog(tab="Heating", group="CTA"));
  parameter Modelica.Units.SI.Time cta_dt_advanced=0
    "Wait time before transition fires"
    annotation (Dialog(tab="Heating", group="CTA"));
  parameter Modelica.Units.SI.Time cta_dt_shed=0
    "Wait time before transition fires"
    annotation (Dialog(tab="Heating", group="CTA"));
  parameter Modelica.Blocks.Interfaces.RealOutput cta_user_deadband=2/1.8
    "Value of Real output" annotation (Dialog(tab="Heating", group="CTA"));
  Modelica.Blocks.Math.Gain gain(k=1/nSeg)
    annotation (Placement(transformation(extent={{12,-60},{32,-40}})));
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor Ttank[20]
    "Temperature of water in the tank"
    annotation (Placement(transformation(extent={{20,-20},{40,0}})));
  Modelica.Blocks.Interfaces.RealOutput y[20]
    annotation (Placement(transformation(extent={{100,40},{120,60}})));
    parameter Integer nSeg(min=1, max=tank_nSeg) = 15 "Number of segements for the HP" annotation (Dialog(tab="Heating", group="Water tank"));
    parameter Integer top_node(min=1, max=tank_nSeg - 1) = 1 "Node at the top of the HP" annotation (Dialog(tab="Heating", group="Water tank"));
    parameter Integer bottom_node(min=top_node, max=tank_nSeg) = 17 "Node at the bottom of the HP" annotation (Dialog(tab="Heating", group="Water tank"));
  parameter Integer tank_nSeg=20 "Number of volume segments";
  Modelica.Blocks.Interfaces.RealInput Tdelta(
    final quantity="ThermodynamicTemperature",
    final unit="K",
    displayUnit="degC")
    "Temperature of evaporator side of heat pump (e.g. outside air temperature if ducted)"
    annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
equation
  connect(booleanToReal.y, heaFlo_res_top.Q_flow)
    annotation (Line(points={{1,70},{40,70}},   color={0,0,127}));
  connect(port_a, tan.port_b) annotation (Line(points={{-100,0},{-70,0},{-70,
          -10},{0,-10}},
                     color={0,127,255}));
  connect(Tambient, preTem.T) annotation (Line(points={{-120,-90},{-84,-90},{
          -84,2},{-52,2},{-52,10},{-42,10}},
                         color={0,0,127}));
  connect(preTem.port, tan.heaPorSid) annotation (Line(points={{-20,10},{-14,
          10},{-14,0},{-5.6,0}},
                            color={191,0,0}));
  connect(tan.port_a, port_b) annotation (Line(points={{0,10},{80,10},{80,0},
          {100,0}}, color={0,127,255}));

  connect(tan.heaPorVol[top_node], heaFlo_res_top.port) annotation (Line(points={{0,0},{
          66,0},{66,70},{60,70}},         color={191,0,0}));
  connect(Tevap, hp_equations.Tevap) annotation (Line(points={{-120,70},{-88,
          70},{-88,-50},{-26,-50},{-26,-61},{-22,-61}}, color={0,0,127}));

for i in tank_nSeg - nSeg + 1:tank_nSeg loop
  connect(tan.heaPorVol[i], heaFlo_hp[i - (tank_nSeg - nSeg + 1) + 1].port) annotation (Line(points={{0,0},{
            66,0},{66,-50},{60,-50}},    color={191,0,0}));
  connect(gain.y, heaFlo_hp[i - (tank_nSeg - nSeg + 1) + 1].Q_flow)
    annotation (Line(points={{33,-50},{40,-50}}, color={0,0,127}));
end for;
  connect(booleanToReal1.y, heaFlo_res_bottom.Q_flow)
    annotation (Line(points={{1,-30},{40,-30}}, color={0,0,127}));
  connect(tan.heaPorVol[bottom_node], heaFlo_res_bottom.port) annotation (Line(points={{0,0},{
          66,0},{66,-30},{60,-30}},             color={191,0,0}));
  connect(summary_state_cta.hp, hp_equations.u) annotation (Line(points={{-39,-75},
          {-26,-75},{-26,-70},{-22,-70}},      color={255,0,255}));
  connect(summary_state_cta.res_bottom, booleanToReal1.u) annotation (Line(
        points={{-39,-67},{-34,-67},{-34,-30},{-22,-30}}, color={255,0,255}));
  connect(summary_state_cta.res_top, booleanToReal.u) annotation (Line(points={{-39,-65},
          {-36,-65},{-36,-14},{-50,-14},{-50,70},{-22,70}},
                                                    color={255,0,255}));
  connect(cta_signal, summary_state_cta.cta_signal) annotation (Line(points={{0,120},
          {0,90},{-60,90},{-60,-40},{-50,-40},{-50,-58}},
                                                color={255,127,0}));
  connect(Tset_user, summary_state_cta.Tset_user_hp) annotation (Line(points={{
          -120,40},{-80,40},{-80,-64},{-62,-64}}, color={0,0,127}));
  connect(Tset_user, summary_state_cta.Tset_user_res) annotation (Line(points={
          {-120,40},{-80,40},{-80,-64},{-70,-64},{-70,-67},{-62,-67}}, color={0,
          0,127}));
  connect(Tevap, summary_state_cta.Tevap) annotation (Line(points={{-120,70},
          {-88,70},{-88,-70},{-62,-70}}, color={0,0,127}));
  connect(hp_equations.Qheat, gain.u)
    annotation (Line(points={{1,-69},{6,-69},{6,-50},{10,-50}},
                                                       color={0,0,127}));

  connect(tan.heaPorVol, Ttank.port) annotation (Line(points={{0,0},{10,0},{10,-10},
          {20,-10}}, color={191,0,0}));
  connect(Ttank.T, y) annotation (Line(points={{41,-10},{72,-10},{72,50},{110,
          50}}, color={0,0,127}));
  connect(Ttank[top_node].T,summary_state_cta.Ttop)  annotation (Line(points={{41,
          -10},{72,-10},{72,-86},{-74,-86},{-74,-76},{-62,-76}}, color={0,0,
          127}));
  connect(Ttank[bottom_node].T,summary_state_cta.Tbottom)  annotation (Line(points={{
          41,-10},{74,-10},{74,-88},{-66,-88},{-66,-79},{-62,-79}}, color={0,
          0,127}));
  connect(Ttank[bottom_node].T, hp_equations.Tbottom) annotation (Line(points={{41,-10},
          {74,-10},{74,-88},{-28,-88},{-28,-65},{-22,-65}}, color={0,0,127}));
  connect(Tdelta, summary_state_cta.Tdelta) annotation (Line(points={{-120,-40},
          {-70,-40},{-70,-61},{-62,-61}}, color={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-100,-120},
            {100,100}}), graphics={
        Rectangle(
          extent={{-40,52},{40,12}},
          lineColor={255,0,0},
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-40,-28},{40,-68}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-40,12},{40,-28}},
          lineColor={255,0,0},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.CrossDiag),
        Rectangle(
          extent={{-40,58},{-50,-76}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-48,60},{50,52}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-48,-68},{50,-76}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-40,12},{40,-28}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-40,60},{-50,-74}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{50,60},{40,-74}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid)}),                      Diagram(
        coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{100,100}})),
    Documentation(info="<html>
<p>Model of a heat pump water heater, derived from a Python model available at .......</p>
<p>The water storage comes frome the <i>Buildings </i>library (<a href=\"modelica://Buildings.Fluid.Storage.StratifiedEnhancedInternalHex\"> Buildings.Fluid.Storage.StratifiedEnhancedInternalHex</a>.), the Heat pump is a generic equation based model.</p>
<p><br>The water storage can be heated up either with :</p>
<ul>
<li>A resistance (alternating between the top node and the bottom node) </li>
<li>A heat pump (heating up between the bottom node and the bottom of the tank)</li>
</ul>
<p>The current model is made with 20 nodes (can be a parameter in future versions):</p>
<ul>
<li>The &quot;bottom node&quot; is the node where the sensor for the HP is connected, The heat flow from the HP is provided to that node and to <i>nSeg - 1</i> other nodes. The resistance is providing heat to that node when it is heating up the bottom part of the tank</li>
<li>The &quot;top node&quot; is where the resistance is connected and heated up when the resistance is heating up the upper part </li>
</ul>
<p><br>All the control for the HP and the resistance are in the &quot;Controls.summary_state_cta&quot; model. The control logic is derived from an existing HPWH and includes CTA-2045 controls.</p>
<p>The equations for the HP are :</p>
</html>"));
end HPWH_virtual;
