within models.HPWH_MPC.Equipment;
model pumps
extends Buildings.Fluid.Interfaces.PartialTwoPort;
  Buildings.Fluid.FixedResistances.Junction jun4(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal={1,1,1},
    dp_nominal={0,0,0})
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-60,0})));
  Buildings.Fluid.Movers.FlowControlled_m_flow pump_storage(
    redeclare package Medium = Buildings.Media.Water,
    use_inputFilter=false,
    m_flow_nominal=1) annotation (Placement(transformation(
        extent={{-20,-10},{0,10}},
        rotation=0)));
  Buildings.Fluid.Movers.FlowControlled_m_flow pump_storage1(
    redeclare package Medium = Buildings.Media.Water,
    use_inputFilter=false,
    m_flow_nominal=1) annotation (Placement(transformation(
        extent={{0,-60},{-20,-40}},
        rotation=0)));
  Modelica.Blocks.Interfaces.RealInput hp_on
    annotation (Placement(transformation(extent={{-140,30},{-100,70}})));
  Modelica.Blocks.Interfaces.RealInput m_flow
    annotation (Placement(transformation(extent={{-140,70},{-100,110}})));
  Modelica.Blocks.Math.Product product1
    annotation (Placement(transformation(extent={{-60,80},{-40,100}})));
  Modelica.Blocks.Math.Product product2
    annotation (Placement(transformation(extent={{-60,20},{-40,40}})));
  Controls.inverse inverse
    annotation (Placement(transformation(extent={{-90,14},{-70,34}})));
  Buildings.Fluid.Actuators.Valves.TwoWayLinear val1(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal=1,
    dpValve_nominal=10,
    use_inputFilter=false)
    annotation (Placement(transformation(extent={{20,-10},{40,10}})));
  Buildings.Fluid.FixedResistances.Junction jun1(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal={1,1,1},
    dp_nominal={0,0,0})
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},
        rotation=0,
        origin={70,0})));
  Buildings.Fluid.Actuators.Valves.TwoWayLinear val(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal=1,
    dpValve_nominal=10,
    use_inputFilter=false)
    annotation (Placement(transformation(extent={{40,-60},{20,-40}})));
equation
  connect(jun4.port_3, pump_storage1.port_b) annotation (Line(points={{-60,-10},
          {-60,-50},{-20,-50}}, color={0,127,255}));
  connect(jun4.port_2, pump_storage.port_a)
    annotation (Line(points={{-50,0},{-20,0}}, color={0,127,255}));
  connect(port_a, jun4.port_1)
    annotation (Line(points={{-100,0},{-70,0}}, color={0,127,255}));
  connect(hp_on, product1.u2) annotation (Line(points={{-120,50},{-80,50},{-80,
          84},{-62,84}}, color={0,0,127}));
  connect(m_flow, product1.u1) annotation (Line(points={{-120,90},{-90,90},{-90,
          96},{-62,96}}, color={0,0,127}));
  connect(product1.y, pump_storage.m_flow_in)
    annotation (Line(points={{-39,90},{-10,90},{-10,12}},
                                                      color={0,0,127}));
  connect(product2.y, pump_storage1.m_flow_in) annotation (Line(points={{-39,30},
          {-30,30},{-30,-28},{-10,-28},{-10,-38}},
                                               color={0,0,127}));
  connect(hp_on, inverse.u) annotation (Line(points={{-120,50},{-96,50},{-96,24},
          {-92,24}}, color={0,0,127}));
  connect(inverse.y, product2.u2)
    annotation (Line(points={{-69,24},{-62,24}}, color={0,0,127}));
  connect(m_flow, product2.u1) annotation (Line(points={{-120,90},{-90,90},{-90,
          36},{-62,36}}, color={0,0,127}));
  connect(product1.y, val1.y) annotation (Line(points={{-39,90},{-10,90},{-10,
          20},{30,20},{30,12}}, color={0,0,127}));
  connect(product2.y, val.y) annotation (Line(points={{-39,30},{-30,30},{-30,
          -28},{30,-28},{30,-38}}, color={0,0,127}));
  connect(pump_storage1.port_a, val.port_b)
    annotation (Line(points={{0,-50},{20,-50}}, color={0,127,255}));
  connect(val1.port_b, jun1.port_1)
    annotation (Line(points={{40,0},{60,0}}, color={0,127,255}));
  connect(pump_storage.port_b, val1.port_a)
    annotation (Line(points={{0,0},{20,0}}, color={0,127,255}));
  connect(val.port_a, jun1.port_3)
    annotation (Line(points={{40,-50},{70,-50},{70,-10}}, color={0,127,255}));
  connect(jun1.port_2, port_b)
    annotation (Line(points={{80,0},{100,0}}, color={0,127,255}));
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
end pumps;
