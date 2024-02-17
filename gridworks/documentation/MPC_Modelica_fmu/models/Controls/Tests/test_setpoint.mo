within models.Controls.Tests;
model test_setpoint
    Modelica.Blocks.Sources.Ramp ramp(duration=5, startTime=1.99)
      annotation (Placement(transformation(extent={{-100,-10},{-80,10}})));
  models.Controls.changing_setpoint changing_setpoint1
    annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
    Modelica.StateGraph.InitialStep initialStep(nOut=1, nIn=1)
      annotation (Placement(transformation(extent={{-80,40},{-60,60}})));
    Modelica.StateGraph.TransitionWithSignal transitionWithSignal
      annotation (Placement(transformation(extent={{-50,40},{-30,60}})));
    Modelica.StateGraph.Step step(nIn=1, nOut=1)
      annotation (Placement(transformation(extent={{-20,40},{0,60}})));
    Modelica.StateGraph.TransitionWithSignal transitionWithSignal1
      annotation (Placement(transformation(extent={{10,40},{30,60}})));
    Modelica.Blocks.Logical.Not not1
      annotation (Placement(transformation(extent={{0,-10},{20,10}})));
    Modelica.StateGraph.Step step1(nIn=1, nOut=1)
      annotation (Placement(transformation(extent={{40,40},{60,60}})));
    Modelica.StateGraph.Transition transition1(enableTimer=true, waitTime=
          10)
      annotation (Placement(transformation(extent={{70,40},{90,60}})));
equation
    connect(ramp.y, changing_setpoint1.u)
      annotation (Line(points={{-79,0},{-62,0}}, color={0,0,127}));
    connect(initialStep.outPort[1], transitionWithSignal.inPort)
      annotation (Line(points={{-59.5,50},{-44,50}}, color={0,0,0}));
    connect(transitionWithSignal.outPort, step.inPort[1])
      annotation (Line(points={{-38.5,50},{-21,50}}, color={0,0,0}));
    connect(step.outPort[1], transitionWithSignal1.inPort)
      annotation (Line(points={{0.5,50},{16,50}}, color={0,0,0}));
    connect(changing_setpoint1.y, transitionWithSignal.condition)
      annotation (Line(points={{-39,0},{-36,0},{-36,30},{-40,30},{-40,38}},
          color={255,0,255}));
    connect(changing_setpoint1.y, not1.u)
      annotation (Line(points={{-39,0},{-2,0}}, color={255,0,255}));
    connect(not1.y, transitionWithSignal1.condition) annotation (Line(
          points={{21,0},{26,0},{26,30},{20,30},{20,38}}, color={255,0,255}));
    connect(transitionWithSignal1.outPort, step1.inPort[1])
      annotation (Line(points={{21.5,50},{39,50}}, color={0,0,0}));
    connect(step1.outPort[1], transition1.inPort)
      annotation (Line(points={{60.5,50},{76,50}}, color={0,0,0}));
    connect(transition1.outPort, initialStep.inPort[1]) annotation (Line(
          points={{81.5,50},{92,50},{92,72},{-90,72},{-90,50},{-81,50}},
          color={0,0,0}));
    annotation (
      Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)),
      experiment(StopTime=10, __Dymola_Algorithm="Dassl"));
end test_setpoint;
