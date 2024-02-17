within models.HPWH_MPC.Equipment;
package Tests "Collection of models that illustrate model use and test models"
extends Modelica.Icons.ExamplesPackage;
  model valves
    Buildings.Fluid.Actuators.Valves.ThreeWayLinear val1(
      redeclare package Medium = Buildings.Media.Water,
      use_inputFilter=false,
      m_flow_nominal=2,
      dpValve_nominal=10) annotation (Placement(transformation(
          extent={{-10,10},{10,-10}},
          rotation=180,
          origin={10,50})));
    Buildings.Fluid.FixedResistances.PressureDrop res(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      dp_nominal=10)
      annotation (Placement(transformation(extent={{40,40},{60,60}})));
    Buildings.Fluid.FixedResistances.PressureDrop res1(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      dp_nominal=10) annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=270,
          origin={10,10})));
    Buildings.Fluid.Sources.Boundary_pT bou1(
      redeclare package Medium = Buildings.Media.Water,
      T=333.15,
      nPorts=1)
      annotation (Placement(transformation(extent={{-80,40},{-60,60}})));
    Buildings.Fluid.Movers.FlowControlled_m_flow mov1(
      redeclare package Medium = Buildings.Media.Water,
      inputType=Buildings.Fluid.Types.InputType.Constant,
      m_flow_nominal=2,
      constantMassFlowRate=2)                      annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={-30,50})));
    Modelica.Blocks.Sources.Step step(
      height=1,
      offset=0,
      startTime=50)
      annotation (Placement(transformation(extent={{-20,70},{0,90}})));
    Buildings.Fluid.Sources.Boundary_pT bou2(redeclare package Medium =
          Buildings.Media.Water, nPorts=1)
      annotation (Placement(transformation(extent={{-10,-10},{10,10}},
          rotation=90,
          origin={10,-30})));
    Buildings.Fluid.Sources.Boundary_pT bou3(redeclare package Medium =
          Buildings.Media.Water, nPorts=1)
      annotation (Placement(transformation(extent={{-10,-10},{10,10}},
          rotation=180,
          origin={90,50})));
  equation
    connect(val1.port_1, res.port_a)
      annotation (Line(points={{20,50},{40,50}}, color={0,127,255}));
    connect(val1.port_3, res1.port_a)
      annotation (Line(points={{10,40},{10,20}}, color={0,127,255}));
    connect(bou1.ports[1], mov1.port_a)
      annotation (Line(points={{-60,50},{-40,50}}, color={0,127,255}));
    connect(mov1.port_b, val1.port_2)
      annotation (Line(points={{-20,50},{0,50}}, color={0,127,255}));
    connect(res1.port_b, bou2.ports[1])
      annotation (Line(points={{10,0},{10,-20}}, color={0,127,255}));
    connect(res.port_b, bou3.ports[1])
      annotation (Line(points={{60,50},{80,50}}, color={0,127,255}));
    connect(step.y, val1.y)
      annotation (Line(points={{1,80},{10,80},{10,62}}, color={0,0,127}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)));
  end valves;

  model test_pumps
    models.HPWH_MPC.Equipment.pumps pumps1(redeclare package Medium =
          Buildings.Media.Water)
      annotation (Placement(transformation(extent={{-20,20},{0,40}})));
    Buildings.Fluid.FixedResistances.PressureDrop res(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      dp_nominal=10)
      annotation (Placement(transformation(extent={{-60,20},{-40,40}})));
    Buildings.Fluid.Sources.Boundary_pT bou(redeclare package Medium =
          Buildings.Media.Water, nPorts=2)
      annotation (Placement(transformation(extent={{-100,20},{-80,40}})));
    Modelica.Blocks.Sources.RealExpression realExpression(y=1)
      annotation (Placement(transformation(extent={{-60,80},{-40,100}})));
    Modelica.Blocks.Sources.Step step(startTime=50)
      annotation (Placement(transformation(extent={{-80,50},{-60,70}})));
    Buildings.Fluid.FixedResistances.PressureDrop res1(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      dp_nominal=10)
      annotation (Placement(transformation(extent={{-60,-80},{-40,-60}})));
    Buildings.Fluid.Sources.Boundary_pT bou1(redeclare package Medium =
          Buildings.Media.Water, nPorts=2)
      annotation (Placement(transformation(extent={{-100,-80},{-80,-60}})));
    Modelica.Blocks.Sources.RealExpression realExpression1(y=1)
      annotation (Placement(transformation(extent={{-60,-20},{-40,0}})));
    Modelica.Blocks.Sources.Step step1(startTime=50)
      annotation (Placement(transformation(extent={{-80,-50},{-60,-30}})));
    pump_bidirectional pumps_bis1
      annotation (Placement(transformation(extent={{-20,-80},{0,-60}})));
  equation
    connect(bou.ports[1], res.port_a) annotation (Line(points={{-80,29},{-70,29},
            {-70,30},{-60,30}},
                              color={0,127,255}));
    connect(res.port_b, pumps1.port_a)
      annotation (Line(points={{-40,30},{-20,30}},
                                                 color={0,127,255}));
    connect(pumps1.port_b, bou.ports[2]) annotation (Line(points={{0,30},{10,30},
            {10,10},{-70,10},{-70,28},{-76,28},{-76,31},{-80,31}}, color={0,127,
            255}));
    connect(realExpression.y, pumps1.m_flow) annotation (Line(points={{-39,90},
            {-30,90},{-30,39},{-22,39}},
                                       color={0,0,127}));
    connect(step.y, pumps1.hp_on) annotation (Line(points={{-59,60},{-34,60},{
            -34,35},{-22,35}},
                             color={0,0,127}));
    connect(bou1.ports[1], res1.port_a) annotation (Line(points={{-80,-71},{-70,
            -71},{-70,-70},{-60,-70}}, color={0,127,255}));
    connect(res1.port_b, pumps_bis1.port_a)
      annotation (Line(points={{-40,-70},{-20,-70}}, color={0,127,255}));
    connect(step1.y, pumps_bis1.hp_on) annotation (Line(points={{-59,-40},{-34,
            -40},{-34,-65},{-22,-65}}, color={0,0,127}));
    connect(pumps_bis1.m_flow, realExpression1.y) annotation (Line(points={{-22,
            -61},{-28,-61},{-28,-10},{-39,-10}}, color={0,0,127}));
    connect(pumps_bis1.port_b, bou1.ports[2]) annotation (Line(points={{0,-70},
            {14,-70},{14,-92},{-72,-92},{-72,-69},{-80,-69}}, color={0,127,255}));
    annotation (
      Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)),
      experiment(StopTime=100, __Dymola_Algorithm="Dassl"));
  end test_pumps;
end Tests;
