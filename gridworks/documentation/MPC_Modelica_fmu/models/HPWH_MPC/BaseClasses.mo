within models.HPWH_MPC;
package BaseClasses "Package with base classes for the Buildings library"
  extends Modelica.Icons.BasesPackage;
  model Partialplant
    Equipment.storage_series storage_series1(
      redeclare package Medium = Buildings.Media.Water,
      VTan=4.5425,
      hTan=1,
      dIns=0.2,
      T_start(displayUnit="degC") = 310)
                annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=270,
          origin={-10,50})));
    Buildings.Fluid.Storage.StratifiedEnhanced tan(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=0.5,
      VTan=4.5425,
      hTan=1,
      dIns=0.2,
      T_start=310)
                annotation (Placement(transformation(extent={{60,20},{80,40}})));
    Buildings.Fluid.FixedResistances.Junction jun(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal={1,1,1},
      dp_nominal={0,0,0})
      annotation (Placement(transformation(extent={{-20,70},{0,90}})));
    Buildings.Fluid.FixedResistances.Junction jun1(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal={1,1,1},
      dp_nominal={0,0,0})
      annotation (Placement(transformation(extent={{20,70},{40,90}})));
    Buildings.Fluid.FixedResistances.Junction jun2(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal={1,1,1},
      dp_nominal={0,0,0}) annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=180,
          origin={30,-90})));
    Buildings.Fluid.Movers.FlowControlled_m_flow pump_load(
      redeclare package Medium = Buildings.Media.Water,
      use_inputFilter=false,
      m_flow_nominal=2) annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=270,
          origin={30,10})));
    Buildings.Fluid.FixedResistances.Junction jun3(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal={1,1,1},
      dp_nominal={0,0,0}) annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=180,
          origin={-10,-90})));
    Buildings.Fluid.Movers.FlowControlled_m_flow pump_hp(
      redeclare package Medium = Buildings.Media.Water,
      use_inputFilter=false,
      m_flow_nominal=1) annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=0,
          origin={-50,80})));
    Buildings.Fluid.Sources.Boundary_pT bou1(
      redeclare package Medium = Buildings.Media.Water,
      use_T_in=true,
      nPorts=2)
      annotation (Placement(transformation(extent={{-40,0},{-60,20}})));
    Buildings.Fluid.Sources.PropertySource_T proSou(use_T_in=true, redeclare
        package Medium = Buildings.Media.Water) annotation (Placement(
          transformation(
          extent={{-10,-10},{10,10}},
          rotation=270,
          origin={30,-30})));
    Buildings.Fluid.Actuators.Valves.TwoWayLinear val(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      dpValve_nominal=10,
      use_inputFilter=false)
      annotation (Placement(transformation(extent={{-40,-100},{-60,-80}})));
    Modelica.Blocks.Interfaces.RealInput storage_m_flow
      annotation (Placement(transformation(extent={{-140,30},{-100,70}})));
    Modelica.Blocks.Interfaces.RealInput load_m_flow
      annotation (Placement(transformation(extent={{-140,-10},{-100,30}})));
    Modelica.Blocks.Interfaces.RealInput hp_T(final quantity="ThermodynamicTemperature",
                                            final unit="K",
                                            displayUnit = "degC",
                                            start=50 + 273.15)
      annotation (Placement(transformation(extent={{-140,-50},{-100,-10}})));
    Modelica.Blocks.Interfaces.RealOutput T[16]
      annotation (Placement(transformation(extent={{100,-10},{120,10}})));
    Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor T_B[4]
      "Temperature of water in the tank"
      annotation (Placement(transformation(extent={{90,40},{110,60}})));
    Modelica.Blocks.Interfaces.RealInput hp_on
      annotation (Placement(transformation(extent={{-140,-90},{-100,-50}})));
    Equipment.pump_bidirectional
                    pump_bidirectional(
                                  redeclare package Medium =
          Buildings.Media.Water) annotation (Placement(transformation(
          extent={{-10,10},{10,-10}},
          rotation=270,
          origin={-10,-50})));
    Modelica.Blocks.Math.Add add(k2=-1)
      annotation (Placement(transformation(extent={{100,-36},{80,-16}})));
    Modelica.Blocks.Sources.RealExpression realExpression(y=20)
      annotation (Placement(transformation(extent={{138,-42},{118,-22}})));
    Buildings.Fluid.Sensors.TemperatureTwoPort senTem(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      T_start=323.15) annotation (Placement(transformation(
          extent={{-10,-10},{10,10}},
          rotation=270,
          origin={30,50})));
    Modelica.Blocks.Logical.GreaterThreshold greaterThreshold(threshold=0.5)
      annotation (Placement(transformation(extent={{-120,86},{-100,106}})));
  equation
    for i in 1:12 loop
      connect(storage_series1.T[i], T[i]);
    end for;
      for i in 13:16 loop
      connect(T_B[i-12].T, T[i]);
      end for;
    connect(jun.port_2, jun1.port_1)
      annotation (Line(points={{0,80},{20,80}}, color={0,127,255}));
    connect(jun1.port_2, tan.port_a)
      annotation (Line(points={{40,80},{70,80},{70,40}},color={0,127,255}));
    connect(jun2.port_1, tan.port_b)
      annotation (Line(points={{40,-90},{70,-90},{70,20}},  color={0,127,255}));
    connect(jun3.port_1, jun2.port_2)
      annotation (Line(points={{0,-90},{20,-90}}, color={0,127,255}));
    connect(pump_hp.port_b, jun.port_1)
      annotation (Line(points={{-40,80},{-20,80}}, color={0,127,255}));
    connect(bou1.ports[1], pump_hp.port_a) annotation (Line(points={{-60,9},{-60,
            12},{-70,12},{-70,80},{-60,80}},
                                         color={0,127,255}));
    connect(pump_load.port_b, proSou.port_a)
      annotation (Line(points={{30,0},{30,-20}}, color={0,127,255}));
    connect(proSou.port_b, jun2.port_3)
      annotation (Line(points={{30,-40},{30,-80}}, color={0,127,255}));
    connect(val.port_a, jun3.port_2)
      annotation (Line(points={{-40,-90},{-20,-90}}, color={0,127,255}));
    connect(jun.port_3, storage_series1.port_a)
      annotation (Line(points={{-10,70},{-10,60}}, color={0,127,255}));
    connect(hp_T, bou1.T_in) annotation (Line(points={{-120,-30},{-34,-30},{-34,14},
            {-38,14}}, color={0,0,127}));
    connect(load_m_flow, pump_load.m_flow_in) annotation (Line(points={{-120,10},{
            -80,10},{-80,28},{50,28},{50,10},{42,10}}, color={0,0,127}));

    connect(tan.heaPorVol, T_B.port) annotation (Line(points={{70,30},{60,30},{60,
            50},{90,50}}, color={191,0,0}));
    connect(hp_on, val.y) annotation (Line(points={{-120,-70},{-50,-70},{-50,-78}},
          color={0,0,127}));
    connect(val.port_b, bou1.ports[2]) annotation (Line(points={{-60,-90},{-70,
            -90},{-70,11},{-60,11}}, color={0,127,255}));
    connect(storage_series1.port_b, pump_bidirectional.port_a)
      annotation (Line(points={{-10,40},{-10,-40}}, color={0,127,255}));
    connect(pump_bidirectional.port_b, jun3.port_3)
      annotation (Line(points={{-10,-60},{-10,-80}}, color={0,127,255}));
    connect(storage_m_flow, pump_bidirectional.m_flow) annotation (Line(points={
            {-120,50},{-50,50},{-50,34},{-19,34},{-19,-38}}, color={0,0,127}));
    connect(hp_on, pump_bidirectional.hp_on) annotation (Line(points={{-120,-70},
            {-50,-70},{-50,-32},{-15,-32},{-15,-38}}, color={0,0,127}));
    connect(add.y, proSou.T_in)
      annotation (Line(points={{79,-26},{42,-26}}, color={0,0,127}));
    connect(add.u2, realExpression.y)
      annotation (Line(points={{102,-32},{117,-32}}, color={0,0,127}));
    connect(jun1.port_3, senTem.port_a)
      annotation (Line(points={{30,70},{30,60}}, color={0,127,255}));
    connect(senTem.port_b, pump_load.port_a)
      annotation (Line(points={{30,40},{30,20}}, color={0,127,255}));
    connect(senTem.T, add.u1) annotation (Line(points={{41,50},{56,50},{56,-10},{
            112,-10},{112,-20},{102,-20}}, color={0,0,127}));
    connect(hp_on, greaterThreshold.u) annotation (Line(points={{-120,-70},{-90,-70},
            {-90,-50},{-140,-50},{-140,96},{-122,96}}, color={0,0,127}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)));
  end Partialplant;
end BaseClasses;
