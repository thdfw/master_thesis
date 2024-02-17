within models.HPWH_MPC;
package Tests "Collection of models that illustrate model use and test models"
extends Modelica.Icons.ExamplesPackage;
  model test_plant
    Modelica.Blocks.Sources.RealExpression realExpression(y=0.1)
      annotation (Placement(transformation(extent={{-80,60},{-60,80}})));
    Modelica.Blocks.Sources.RealExpression realExpression1(y=0.2)
      annotation (Placement(transformation(extent={{-80,40},{-60,60}})));
    Modelica.Blocks.Sources.RealExpression realExpression2(y=50 + 273.15)
      annotation (Placement(transformation(extent={{-80,20},{-60,40}})));
    Modelica.Blocks.Sources.Step step(
      height=-1,
      offset=1,
      startTime=1000)
      annotation (Placement(transformation(extent={{-80,0},{-60,20}})));
    plant_hp_variable plant_b1
      annotation (Placement(transformation(extent={{-20,20},{0,40}})));
  equation
    connect(realExpression.y, plant_b1.storage_m_flow) annotation (Line(points=
            {{-59,70},{-36,70},{-36,35},{-22,35}}, color={0,0,127}));
    connect(realExpression1.y, plant_b1.load_m_flow) annotation (Line(points={{
            -59,50},{-44,50},{-44,31},{-22,31}}, color={0,0,127}));
    connect(realExpression2.y, plant_b1.hp_T) annotation (Line(points={{-59,30},
            {-46,30},{-46,27},{-22,27}}, color={0,0,127}));
    connect(step.y, plant_b1.hp_on) annotation (Line(points={{-59,10},{-52,10},
            {-52,23},{-22,23}}, color={0,0,127}));
    annotation (
      Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)),
      experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
  end test_plant;

  model test_fmu
    Modelica.Blocks.Sources.RealExpression realExpression(y=0.1)
      annotation (Placement(transformation(extent={{-80,60},{-60,80}})));
    Modelica.Blocks.Sources.RealExpression realExpression1(y=0.2)
      annotation (Placement(transformation(extent={{-80,40},{-60,60}})));
    Modelica.Blocks.Sources.RealExpression realExpression2(y=50 + 273.15)
      annotation (Placement(transformation(extent={{-80,20},{-60,40}})));
    Modelica.Blocks.Sources.RealExpression realExpression3(y=60 + 273.15)
      annotation (Placement(transformation(extent={{-80,80},{-60,100}})));
    BaseClasses.Partialplant plant_b1
      annotation (Placement(transformation(extent={{-20,20},{0,40}})));
    Modelica.Blocks.Interfaces.RealInput hp_on
      annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
    Modelica.Blocks.Interfaces.RealOutput T[16]
      annotation (Placement(transformation(extent={{100,-10},{120,10}})));
  equation
    connect(realExpression3.y, plant_b1.T_load) annotation (Line(points={{-59,
            90},{-28,90},{-28,39},{-22,39}}, color={0,0,127}));
    connect(realExpression.y, plant_b1.storage_m_flow) annotation (Line(points=
            {{-59,70},{-36,70},{-36,35},{-22,35}}, color={0,0,127}));
    connect(realExpression1.y, plant_b1.load_m_flow) annotation (Line(points={{
            -59,50},{-44,50},{-44,31},{-22,31}}, color={0,0,127}));
    connect(realExpression2.y, plant_b1.hp_T) annotation (Line(points={{-59,30},
            {-46,30},{-46,27},{-22,27}}, color={0,0,127}));
    connect(hp_on, plant_b1.hp_on) annotation (Line(points={{-120,0},{-40,0},{
            -40,23},{-22,23}}, color={0,0,127}));
    connect(plant_b1.T, T) annotation (Line(points={{1,30},{40,30},{40,0},{110,
            0}}, color={0,0,127}));
    annotation (
      Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)),
      experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
  end test_fmu;

  model test_fmu_2
    Modelica.Blocks.Sources.RealExpression realExpression1(y=0.2)
      annotation (Placement(transformation(extent={{-80,40},{-60,60}})));
    Modelica.Blocks.Sources.RealExpression realExpression2(y=50 + 273.15)
      annotation (Placement(transformation(extent={{-80,20},{-60,40}})));
    Modelica.Blocks.Sources.RealExpression realExpression3(y=60 + 273.15)
      annotation (Placement(transformation(extent={{-80,80},{-60,100}})));
    BaseClasses.Partialplant plant_b1
      annotation (Placement(transformation(extent={{-20,20},{0,40}})));
    Modelica.Blocks.Interfaces.RealInput hp_on
      annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
    Modelica.Blocks.Interfaces.RealOutput T[16]
      annotation (Placement(transformation(extent={{100,-10},{120,10}})));
    Modelica.Blocks.Interfaces.RealInput storage_m_flow
      annotation (Placement(transformation(extent={{-140,50},{-100,90}})));
  equation
    connect(realExpression3.y, plant_b1.T_load) annotation (Line(points={{-59,
            90},{-28,90},{-28,39},{-22,39}}, color={0,0,127}));
    connect(realExpression1.y, plant_b1.load_m_flow) annotation (Line(points={{
            -59,50},{-44,50},{-44,31},{-22,31}}, color={0,0,127}));
    connect(realExpression2.y, plant_b1.hp_T) annotation (Line(points={{-59,30},
            {-46,30},{-46,27},{-22,27}}, color={0,0,127}));
    connect(hp_on, plant_b1.hp_on) annotation (Line(points={{-120,0},{-40,0},{
            -40,23},{-22,23}}, color={0,0,127}));
    connect(plant_b1.T, T) annotation (Line(points={{1,30},{40,30},{40,0},{110,
            0}}, color={0,0,127}));
    connect(storage_m_flow, plant_b1.storage_m_flow) annotation (Line(points={{
            -120,70},{-34,70},{-34,35},{-22,35}}, color={0,0,127}));
    annotation (
      Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)),
      experiment(StopTime=2000, __Dymola_Algorithm="Dassl"));
  end test_fmu_2;
end Tests;
