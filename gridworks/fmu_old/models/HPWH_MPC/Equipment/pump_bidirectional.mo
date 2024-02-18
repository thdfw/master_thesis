within models.HPWH_MPC.Equipment;
model pump_bidirectional
extends Buildings.Fluid.Interfaces.PartialTwoPort;
  Buildings.Fluid.Movers.FlowControlled_m_flow pump_storage(
    redeclare package Medium = Buildings.Media.Water,
    use_inputFilter=false,
    m_flow_nominal=1) annotation (Placement(transformation(
        extent={{-40,-80},{-20,-60}},
        rotation=0)));
  Modelica.Blocks.Interfaces.RealInput hp_on
    annotation (Placement(transformation(extent={{-140,30},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput m_flow
    annotation (Placement(transformation(extent={{-140,70},{-100,110}})));
  Buildings.Fluid.FixedResistances.Junction jun1(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal={1,1,1},
    dp_nominal={0,0,0})
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-70,0})));
  Buildings.Fluid.Actuators.Valves.ThreeWayLinear val(
    redeclare package Medium = Buildings.Media.Water,
    use_inputFilter=false,
    m_flow_nominal=2,
    dpValve_nominal=10) annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=270,
        origin={-70,-40})));
  Buildings.Fluid.FixedResistances.Junction jun2(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal={1,1,1},
    dp_nominal={0,0,0})
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},
        rotation=0,
        origin={50,0})));
  Buildings.Fluid.Actuators.Valves.ThreeWayLinear val1(
    redeclare package Medium = Buildings.Media.Water,
    use_inputFilter=false,
    m_flow_nominal=2,
    dpValve_nominal=10) annotation (Placement(transformation(extent={{-10,-10},
            {10,10}}, rotation=270)));
equation
  connect(port_a, jun1.port_1)
    annotation (Line(points={{-100,0},{-80,0}}, color={0,127,255}));
  connect(val.port_2, pump_storage.port_a) annotation (Line(points={{-70,-50},{
          -70,-70},{-40,-70}}, color={0,127,255}));
  connect(val.port_3, jun2.port_3)
    annotation (Line(points={{-60,-40},{50,-40},{50,-10}}, color={0,127,255}));
  connect(jun2.port_2, port_b)
    annotation (Line(points={{60,0},{100,0}}, color={0,127,255}));
  connect(jun1.port_3, val.port_1)
    annotation (Line(points={{-70,-10},{-70,-30}}, color={0,127,255}));
  connect(jun1.port_2, val1.port_3)
    annotation (Line(points={{-60,0},{-10,0}}, color={0,127,255}));
  connect(pump_storage.port_b, val1.port_2)
    annotation (Line(points={{-20,-70},{0,-70},{0,-10}}, color={0,127,255}));
  connect(val1.port_1, jun2.port_1) annotation (Line(points={{0,10},{0,20},{30,
          20},{30,0},{40,0}}, color={0,127,255}));
  connect(hp_on, val.y) annotation (Line(points={{-120,50},{-90,50},{-90,-40},{
          -82,-40}}, color={0,0,127}));
  connect(hp_on, val1.y) annotation (Line(points={{-120,50},{20,50},{20,0},{12,
          0}}, color={0,0,127}));
  connect(m_flow, pump_storage.m_flow_in)
    annotation (Line(points={{-120,90},{-30,90},{-30,-58}}, color={0,0,127}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
        Rectangle(
          extent={{-60,60},{60,40}},
          lineColor={0,0,0},
          fillColor={0,127,255},
          fillPattern=FillPattern.HorizontalCylinder),
        Rectangle(
          extent={{-60,-40},{60,-60}},
          lineColor={0,0,0},
          fillColor={0,127,255},
          fillPattern=FillPattern.HorizontalCylinder),
        Rectangle(
          extent={{-100,10},{-64,-10}},
          lineColor={0,0,0},
          fillColor={0,127,255},
          fillPattern=FillPattern.HorizontalCylinder),
        Ellipse(
          extent={{-30,80},{32,20}},
          lineColor={0,0,0},
          fillPattern=FillPattern.Sphere,
          fillColor={0,100,199}),
        Polygon(
          points={{0,80},{0,20},{32,52},{0,80}},
          lineColor={0,0,0},
          pattern=LinePattern.None,
          fillPattern=FillPattern.HorizontalCylinder,
          fillColor={255,255,255}),
        Ellipse(
          extent={{4,58},{20,42}},
          lineColor={0,0,0},
          fillPattern=FillPattern.Sphere,
          visible=energyDynamics <> Modelica.Fluid.Types.Dynamics.SteadyState,
          fillColor={0,100,199}),
        Ellipse(
          extent={{-30,-20},{32,-80}},
          lineColor={0,0,0},
          fillPattern=FillPattern.Sphere,
          fillColor={0,100,199}),
        Polygon(
          points={{-16,30},{-16,-30},{14,0},{-16,30}},
          lineColor={0,0,0},
          pattern=LinePattern.None,
          fillPattern=FillPattern.HorizontalCylinder,
          fillColor={255,255,255},
          origin={-16,-50},
          rotation=180),
        Ellipse(
          extent={{-20,-42},{-4,-58}},
          lineColor={0,0,0},
          fillPattern=FillPattern.Sphere,
          visible=energyDynamics <> Modelica.Fluid.Types.Dynamics.SteadyState,
          fillColor={0,100,199}),
        Rectangle(
          extent={{64,10},{100,-10}},
          lineColor={0,0,0},
          fillColor={0,127,255},
          fillPattern=FillPattern.HorizontalCylinder),
        Rectangle(
          extent={{-60,10},{60,-10}},
          lineColor={0,0,0},
          fillColor={0,127,255},
          fillPattern=FillPattern.HorizontalCylinder,
          origin={60,0},
          rotation=90),
        Rectangle(
          extent={{-60,10},{60,-10}},
          lineColor={0,0,0},
          fillColor={0,127,255},
          fillPattern=FillPattern.HorizontalCylinder,
          origin={-60,0},
          rotation=90)}),                                        Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end pump_bidirectional;
