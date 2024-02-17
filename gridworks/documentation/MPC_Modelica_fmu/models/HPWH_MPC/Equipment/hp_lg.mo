within models.HPWH_MPC.Equipment;
model hp_lg
  Modelica.Blocks.Tables.CombiTable1Ds mHP_flow_tab(
    tableOnFile=false,
    table=[7,34.5/60; 10,34.5/60; 13,34.5/60; 15,34.5/60; 18,34.5/60; 20,34.5/
        60; 22,34.5/60; 30,34.5/60; 35,34.5/60; 40,34.5/60; 45,34.5/60; 50,21.6
        /60; 55,21.6/60; 60,17.3/60; 65,17.3/60],
    smoothness=Modelica.Blocks.Types.Smoothness.ConstantSegments,
    extrapolation=Modelica.Blocks.Types.Extrapolation.NoExtrapolation)
    "First column is LWT set points, second column is water flow rate in (LPM)*(1kg/L)*(1min/60sec)"
    annotation (Placement(transformation(extent={{-54,50},{-34,70}})));
  Modelica.Blocks.Interfaces.RealInput TSet
    annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
  Modelica.Blocks.Interfaces.RealOutput mHP_flow annotation (Placement(
        transformation(extent={{100,-10},{120,10}}), iconTransformation(extent={{100,-10},
            {120,10}})));
  Modelica.Blocks.Interfaces.BooleanInput IO
    annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
  Controls.Switch_onoff switch1
    annotation (Placement(transformation(extent={{40,-10},{60,10}})));
equation
  connect(TSet, mHP_flow_tab.u)
    annotation (Line(points={{-120,60},{-56,60}}, color={0,0,127}));
  connect(mHP_flow_tab.y[1], switch1.u1) annotation (Line(points={{-33,60},{30,
          60},{30,8},{38,8}}, color={0,0,127}));
  connect(IO, switch1.u2) annotation (Line(points={{-120,-60},{-60,-60},{-60,0},
          {38,0}}, color={255,0,255}));
  connect(switch1.y, mHP_flow)
    annotation (Line(points={{61,0},{110,0}}, color={0,0,127}));
  annotation (Icon(graphics={Text(
          extent={{-78,64},{70,-50}},
          textColor={28,108,200},
          textString="MassFlow Controller"), Rectangle(
          extent={{-100,100},{100,-100}},
          lineColor={28,108,200},
          lineThickness=1)}));
end hp_lg;
