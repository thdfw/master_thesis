within models.HPWH;
package Controls
  "\"Control models not present neither in Modelica nor Buildings libraries\""
  extends Modelica.Icons.Package;
  package model_a
    model summary_state_cta
      Modelica.Blocks.Interfaces.BooleanOutput res_top
        annotation (Placement(transformation(extent={{100,40},{120,60}})));
      Modelica.Blocks.Interfaces.BooleanOutput hp
        annotation (Placement(transformation(extent={{100,-60},{120,-40}})));
      res_state res_state1(res_deadband=res_deadband, res_deadband_hpactive=
            res_deadband_hpactive)
        annotation (Placement(transformation(extent={{-40,40},{-20,60}})));
      Modelica.Blocks.Logical.GreaterThreshold
                                        greaterThreshold(
                                                      threshold=cut_temperature)
        annotation (Placement(transformation(extent={{-60,0},{-40,20}})));
      parameter Modelica.Units.SI.Temperature cut_temperature=5 + 273.15
        "Comparison with respect to threshold"
    annotation (Dialog(group="HP"));
      deadband deadband1(deadband_hp_recent=deadband_hp_recent, deadband_hp=
            deadband_hp,
        hp_timewindow=hp_timewindow)
        annotation (Placement(transformation(extent={{-60,-38},{-40,-18}})));
      Modelica.Blocks.Interfaces.RealInput Tset_user_hp(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
      Modelica.Blocks.Interfaces.RealInput Ttop(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Temperature at the top of the tank"
        annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
      Modelica.Blocks.Interfaces.RealInput Tbottom(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Temperature at the bottom of the tank"
        annotation (Placement(transformation(extent={{-140,-110},{-100,-70}})));
      Modelica.Blocks.Interfaces.RealInput Tset_user_res(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,10},{-100,50}})));
      Modelica.Blocks.Interfaces.RealInput Tevap(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      inner Modelica.StateGraph.StateGraphRoot stateGraphRoot
        annotation (Placement(transformation(extent={{80,80},{100,100}})));
      parameter Modelica.Units.SI.Time cycle_time=300
        "Wait time before transition fires"
    annotation (Dialog(group="HP"));

      parameter Modelica.Blocks.Interfaces.RealOutput deadband_hp=0.0
        "Value of Real output"
    annotation (Dialog(group="HP"));
      parameter Modelica.Blocks.Interfaces.RealOutput deadband_hp_recent=0.0
        "Value of Real output"
    annotation (Dialog(group="HP"));
      parameter Modelica.Blocks.Interfaces.RealOutput deadband_low_stratification=5
        "Value of Real output"
    annotation (Dialog(group="HP"));
      parameter Real res_deadband=5 "Output signal for true Boolean input"
    annotation (Dialog(group="Resistance"));
      parameter Real res_deadband_hpactive=5
        "Output signal for false Boolean input"
    annotation (Dialog(group="Resistance"));
      parameter Modelica.Units.SI.Time hp_timewindow=0
        "Wait time before transition fires" annotation (Dialog(group="HP"));
      Modelica.Blocks.Interfaces.BooleanOutput res_bottom
        annotation (Placement(transformation(extent={{100,20},{120,40}})));
      hp_state_cta hp_state_cta1(
        cycle_time=cycle_time,
        deadband_low_stratification=deadband_low_stratification,
        cta_dt_loadup=cta_dt_loadup,
        cta_dt_advanced=cta_dt_advanced,
        cta_dt_shed=cta_dt_shed,
        cta_user_deadband=cta_user_deadband)
        annotation (Placement(transformation(extent={{40,-60},{60,-40}})));
      Modelica.Blocks.Interfaces.IntegerInput cta_signal annotation (Placement(
            transformation(
            extent={{-20,-20},{20,20}},
            rotation=270,
            origin={0,120})));
      parameter Modelica.Units.SI.Time cta_dt_loadup=0
        "Wait time before transition fires" annotation (Dialog(group="CTA"));
      parameter Modelica.Units.SI.Time cta_dt_advanced=0
        "Wait time before transition fires" annotation (Dialog(group="CTA"));
      parameter Modelica.Units.SI.Time cta_dt_shed=0
        "Wait time before transition fires" annotation (Dialog(group="CTA"));
      parameter Modelica.Blocks.Interfaces.RealOutput cta_user_deadband=2/1.8
        "Value of Real output" annotation (Dialog(group="CTA"));
      Modelica.Blocks.Interfaces.RealInput Tdelta
        "Temperature variation around the user setpoint"
        annotation (Placement(transformation(extent={{-140,70},{-100,110}})));
      Modelica.Blocks.Math.Add add_res
        annotation (Placement(transformation(extent={{-80,64},{-60,84}})));
    equation
      connect(greaterThreshold.y, res_state1.cutoff) annotation (Line(points={{
              -39,10},{0,10},{0,30},{-60,30},{-60,50},{-42,50}}, color={255,0,
              255}));
      connect(deadband1.y, res_state1.hp_deadband) annotation (Line(points={{-39,-28},
              {-20,-28},{-20,-10},{-76,-10},{-76,53},{-42,53}},        color={0,
              0,127}));
      connect(Ttop, res_state1.TTop) annotation (Line(points={{-120,-60},{-90,
              -60},{-90,44},{-42,44}}, color={0,0,127}));
      connect(Tbottom, res_state1.TBottom) annotation (Line(points={{-120,-90},
              {-84,-90},{-84,41},{-42,41}}, color={0,0,127}));
      connect(Tevap, greaterThreshold.u) annotation (Line(points={{-120,0},{-94,
              0},{-94,10},{-62,10}}, color={0,0,127}));
      connect(res_state1.top, res_top) annotation (Line(points={{-19,59},{92,59},
              {92,50},{110,50}}, color={255,0,255}));
      connect(res_state1.bottom, res_bottom) annotation (Line(points={{-19,56},
              {88,56},{88,30},{110,30}}, color={255,0,255}));
      connect(hp_state_cta1.y, hp)
        annotation (Line(points={{61,-50},{110,-50}}, color={255,0,255}));
      connect(cta_signal, hp_state_cta1.cta_signal) annotation (Line(points={{0,120},
              {0,70},{57,70},{57,-38}},          color={255,127,0}));
      connect(hp_state_cta1.y, res_state1.hp_active) annotation (Line(points={{
              61,-50},{66,-50},{66,34},{-50,34},{-50,47},{-42,47}}, color={255,
              0,255}));
      connect(res_state1.y, hp_state_cta1.res) annotation (Line(points={{-19,50},
              {30,50},{30,-51},{38,-51}}, color={255,0,255}));
      connect(greaterThreshold.y, hp_state_cta1.cutoff) annotation (Line(points={{-39,10},
              {0,10},{0,-53},{38,-53}},          color={255,0,255}));
      connect(deadband1.y, hp_state_cta1.deadband) annotation (Line(points={{-39,-28},
              {20,-28},{20,-47},{38,-47}},          color={0,0,127}));
      connect(Tbottom,hp_state_cta1.Tbottom)  annotation (Line(points={{-120,
              -90},{30,-90},{30,-60},{38,-60}}, color={0,0,127}));
      connect(Ttop,hp_state_cta1.Ttop)  annotation (Line(points={{-120,-60},{
              -20,-60},{-20,-56},{38,-56}}, color={0,0,127}));
      connect(Tdelta, add_res.u1) annotation (Line(points={{-120,90},{-92,90},{
              -92,80},{-82,80}}, color={0,0,127}));
      connect(Tset_user_res, add_res.u2) annotation (Line(points={{-120,30},{-92,
              30},{-92,68},{-82,68}}, color={0,0,127}));
      connect(add_res.y, res_state1.Tset_res) annotation (Line(points={{-59,74},
              {-52,74},{-52,56},{-42,56}}, color={0,0,127}));
      connect(Tdelta, hp_state_cta1.Tdelta) annotation (Line(points={{-120,90},
              {26,90},{26,-41},{38,-41}}, color={0,0,127}));
      connect(hp_state_cta1.Tset_user_hp, Tset_user_hp) annotation (Line(points
            ={{38,-44},{-80,-44},{-80,60},{-120,60}}, color={0,0,127}));
      connect(add_res.y, deadband1.Tset_hp) annotation (Line(points={{-59,74},{
              -52,74},{-52,56},{-70,56},{-70,-28},{-62,-28}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
                extent={{-100,100},{100,-100}},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
              Rectangle(extent={{-84,16},{-46,-18}}),
              Line(points={{-2,32},{-2,-38}}),
              Rectangle(extent={{46,16},{84,-18}}),
              Polygon(
                points={{-14,6},{-2,0},{-14,-6},{-14,6}},
                fillPattern=FillPattern.Solid),
              Line(points={{-46,0},{-14,0}}),
              Polygon(
                points={{34,6},{46,0},{34,-6},{34,6}},
                fillPattern=FillPattern.Solid),
              Line(points={{-2,0},{34,0}}),
              Text(
                extent={{-200,106},{200,146}},
                textString="%name",
                textColor={0,0,255})}),       Diagram(coordinateSystem(
              preserveAspectRatio=false)),
        Documentation(info="<html>
<p>Central control for both the HP and the resistance.</p>
<p>Control takes as inputs the setpoint temperatures for the HP and the resistance, and the temperature from the sensors at the top and the bottom of the tank.</p>
<p>It also allows controlas from a cta-2045 module.</p>
<p>As output, there are the different boolean signals for the HP, the top resistance and the bottom resistance.</p>
</html>"));
    end summary_state_cta;

    model res_state
      Buildings.Controls.OBC.CDL.Interfaces.BooleanInput cutoff
        "Active resistance"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.StateGraph.InitialStep initialStep(nOut=2, nIn=2)
        annotation (Placement(transformation(extent={{-40,-40},{-20,-20}})));
      Modelica.Blocks.Interfaces.RealInput Tset_hp(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,70},{-100,110}})));
      Modelica.Blocks.Interfaces.RealInput TTop(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Temperature at the top of the tank"
        annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
      Modelica.Blocks.Interfaces.RealInput TBottom(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Temperature at the bottom of the tank"
        annotation (Placement(transformation(extent={{-140,-110},{-100,-70}})));
      Modelica.Blocks.Interfaces.RealInput Tset_res(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
      Modelica.Blocks.Sources.RealExpression realExpression(y=Tset_hp - 0.5)
        annotation (Placement(transformation(extent={{-22,182},{-2,202}})));
      Modelica.Blocks.Logical.Greater greater
        annotation (Placement(transformation(extent={{20,190},{40,210}})));
      Modelica.Blocks.Logical.Greater greater1
        annotation (Placement(transformation(extent={{20,160},{40,180}})));
      Modelica.Blocks.Logical.Not not1
        annotation (Placement(transformation(extent={{20,80},{40,100}})));
      Modelica.Blocks.Logical.And and1
        annotation (Placement(transformation(extent={{60,180},{80,200}})));
      Modelica.Blocks.Logical.And and3
        annotation (Placement(transformation(extent={{-10,-130},{10,-110}})));
      Modelica.Blocks.Logical.Less less
        annotation (Placement(transformation(extent={{-20,130},{0,150}})));
      Modelica.Blocks.Interfaces.RealInput hp_deadband
                            "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,10},{-100,50}})));
      Modelica.Blocks.Logical.Less less1
        annotation (Placement(transformation(extent={{-20,100},{0,120}})));
      Modelica.Blocks.Logical.Or or1
        annotation (Placement(transformation(extent={{20,120},{40,140}})));
      Modelica.Blocks.Sources.RealExpression realExpression1(y=Tset_res - 1)
        annotation (Placement(transformation(extent={{20,-120},{40,-100}})));
      Modelica.Blocks.Logical.Greater greater2
        annotation (Placement(transformation(extent={{60,-112},{80,-92}})));
      Modelica.StateGraph.StepWithSignal
                               stepWithSignal1(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{20,-40},{40,-20}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal1
        annotation (Placement(transformation(extent={{50,-40},{70,-20}})));
      Modelica.StateGraph.StepWithSignal
                               stepWithSignal2(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{80,-40},{100,-20}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal2
        annotation (Placement(transformation(extent={{120,-40},{140,-20}})));
      Modelica.Blocks.Sources.RealExpression realExpression2(y=Tset_res - 1)
        annotation (Placement(transformation(extent={{20,-178},{40,-158}})));
      Modelica.Blocks.Logical.Greater greater3
        annotation (Placement(transformation(extent={{60,-170},{80,-150}})));
      Modelica.Blocks.Logical.Greater greater4
        annotation (Placement(transformation(extent={{62,-140},{82,-120}})));
      Modelica.Blocks.Sources.RealExpression realExpression3(y=Tset_res + 1)
        annotation (Placement(transformation(extent={{22,-148},{42,-128}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal4
        annotation (Placement(transformation(extent={{-10,-40},{10,-20}})));
      Modelica.Blocks.Math.BooleanToReal deadband_res(realTrue=res_deadband,
          realFalse=res_deadband_hpactive) annotation (Placement(transformation(
              extent={{-120,-140},{-100,-120}})));
      parameter Real res_deadband=5 "Output signal for true Boolean input";
      parameter Real res_deadband_hpactive=5
        "Output signal for false Boolean input";
      Modelica.Blocks.Logical.Less less3
        annotation (Placement(transformation(extent={{-40,-130},{-20,-110}})));
      Buildings.Controls.OBC.CDL.Interfaces.BooleanInput hp_active
        "Active resistance"
        annotation (Placement(transformation(extent={{-140,-50},{-100,-10}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal5(
          enableTimer=true, waitTime=60)
        annotation (Placement(transformation(extent={{-10,20},{10,40}})));
      Modelica.Blocks.Math.Add add(k2=-1)
        annotation (Placement(transformation(extent={{-60,120},{-40,140}})));
      Modelica.StateGraph.StepWithSignal
                               stepWithSignal3(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{20,20},{40,40}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal6
        annotation (Placement(transformation(extent={{60,20},{80,40}})));
      Modelica.Blocks.Logical.And and2
        annotation (Placement(transformation(extent={{60,120},{80,140}})));
      Modelica.Blocks.Interfaces.BooleanOutput y
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.MathBoolean.Or or2(nu=3)
        annotation (Placement(transformation(extent={{160,-80},{180,-60}})));
      Modelica.Blocks.MathBoolean.Or or3(nu=2)
        annotation (Placement(transformation(extent={{100,-150},{120,-130}})));
      Modelica.Blocks.Math.Add add1(k2=-1)
        annotation (Placement(transformation(extent={{-80,-180},{-60,-160}})));
      Modelica.Blocks.Logical.Greater greater5
        annotation (Placement(transformation(extent={{20,250},{40,270}})));
      Modelica.StateGraph.InitialStep initialStep1(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{100,260},{120,280}})));
      Modelica.StateGraph.StepWithSignal
                               stepWithSignal4(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{160,260},{180,280}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal3
        annotation (Placement(transformation(extent={{130,260},{150,280}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal7
        annotation (Placement(transformation(extent={{190,260},{210,280}})));
      Modelica.Blocks.Logical.Greater greater6
        annotation (Placement(transformation(extent={{20,220},{40,240}})));
      Modelica.StateGraph.StepWithSignal
                               stepWithSignal5(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{220,260},{240,280}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal8
        annotation (Placement(transformation(extent={{250,260},{270,280}})));
      Modelica.Blocks.Interfaces.BooleanOutput top
        annotation (Placement(transformation(extent={{100,80},{120,100}})));
      Modelica.Blocks.Interfaces.BooleanOutput bottom
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      Modelica.Blocks.MathBoolean.Or or4(nu=3)
        annotation (Placement(transformation(extent={{178,120},{198,140}})));
      Modelica.Blocks.Logical.And and4
        annotation (Placement(transformation(extent={{220,120},{240,140}})));
      Modelica.Blocks.Logical.And and5
        annotation (Placement(transformation(extent={{240,180},{260,200}})));
    equation
      connect(realExpression.y, greater.u2)
        annotation (Line(points={{-1,192},{18,192}},  color={0,0,127}));
      connect(realExpression.y, greater1.u2) annotation (Line(points={{-1,192},
              {8,192},{8,162},{18,162}},     color={0,0,127}));
      connect(greater.y, and1.u1) annotation (Line(points={{41,200},{48,200},{
              48,190},{58,190}}, color={255,0,255}));
      connect(greater1.y, and1.u2) annotation (Line(points={{41,170},{48,170},{
              48,182},{58,182}}, color={255,0,255}));
      connect(less1.y, or1.u2) annotation (Line(points={{1,110},{8,110},{8,122},
              {18,122}}, color={255,0,255}));
      connect(less.y, or1.u1) annotation (Line(points={{1,140},{8,140},{8,130},
              {18,130}}, color={255,0,255}));
      connect(realExpression1.y, greater2.u2)
        annotation (Line(points={{41,-110},{58,-110}}, color={0,0,127}));
      connect(TTop, greater2.u1) annotation (Line(points={{-120,-60},{-80,-60},
              {-80,-80},{48,-80},{48,-102},{58,-102}}, color={0,0,127}));
      connect(stepWithSignal1.outPort[1], transitionWithSignal1.inPort)
        annotation (Line(points={{40.5,-30},{56,-30}}, color={0,0,0}));
      connect(greater2.y, transitionWithSignal1.condition) annotation (Line(
            points={{81,-102},{86,-102},{86,-74},{60,-74},{60,-42}}, color={255,
              0,255}));
      connect(transitionWithSignal1.outPort, stepWithSignal2.inPort[1])
        annotation (Line(points={{61.5,-30},{79,-30}}, color={0,0,0}));
      connect(realExpression3.y, greater4.u2)
        annotation (Line(points={{43,-138},{60,-138}}, color={0,0,127}));
      connect(realExpression2.y, greater3.u2)
        annotation (Line(points={{41,-168},{58,-168}}, color={0,0,127}));
      connect(stepWithSignal2.outPort[1], transitionWithSignal2.inPort)
        annotation (Line(points={{100.5,-30},{126,-30}},
                     color={0,0,0}));
      connect(transitionWithSignal4.outPort, stepWithSignal1.inPort[1])
        annotation (Line(points={{1.5,-30},{19,-30}}, color={0,0,0}));
      connect(initialStep.outPort[1], transitionWithSignal4.inPort) annotation (
         Line(points={{-19.5,-30.125},{-14,-30.125},{-14,-30},{-4,-30}}, color=
              {0,0,0}));
      connect(initialStep.inPort[1], transitionWithSignal2.outPort) annotation (
         Line(points={{-41,-30.25},{-46,-30.25},{-46,48},{140,48},{140,-30},{
              131.5,-30}},
            color={0,0,0}));
      connect(less3.y, and3.u1)
        annotation (Line(points={{-19,-120},{-12,-120}}, color={255,0,255}));
      connect(cutoff, and3.u2) annotation (Line(points={{-120,0},{-60,0},{-60,
              -140},{-16,-140},{-16,-128},{-12,-128}}, color={255,0,255}));
      connect(and3.y, transitionWithSignal4.condition) annotation (Line(points=
              {{11,-120},{16,-120},{16,-50},{0,-50},{0,-42}}, color={255,0,255}));
      connect(TTop, greater4.u1) annotation (Line(points={{-120,-60},{-80,-60},
              {-80,-80},{48,-80},{48,-130},{60,-130}}, color={0,0,127}));
      connect(TBottom, greater3.u1) annotation (Line(points={{-120,-90},{-74,
              -90},{-74,-150},{-8,-150},{-8,-160},{58,-160}},
                                          color={0,0,127}));
      connect(deadband_res.y, less1.u2) annotation (Line(points={{-99,-130},{
              -64,-130},{-64,102},{-22,102}}, color={0,0,127}));
      connect(TTop, less1.u1) annotation (Line(points={{-120,-60},{-80,-60},{
              -80,110},{-22,110}}, color={0,0,127}));
      connect(TBottom, less.u1) annotation (Line(points={{-120,-90},{-74,-90},{
              -74,146},{-34,146},{-34,140},{-22,140}}, color={0,0,127}));
      connect(Tset_hp, add.u1) annotation (Line(points={{-120,90},{-98,90},{-98,
              136},{-62,136}}, color={0,0,127}));
      connect(hp_deadband, add.u2) annotation (Line(points={{-120,30},{-88,30},
              {-88,124},{-62,124}}, color={0,0,127}));
      connect(add.y, less.u2) annotation (Line(points={{-39,130},{-32,130},{-32,
              132},{-22,132}}, color={0,0,127}));
      connect(transitionWithSignal5.outPort, stepWithSignal3.inPort[1])
        annotation (Line(points={{1.5,30},{19,30}}, color={0,0,0}));
      connect(TBottom, greater.u1) annotation (Line(points={{-120,-90},{-74,-90},
              {-74,204},{6,204},{6,200},{18,200}}, color={0,0,127}));
      connect(TTop, greater1.u1) annotation (Line(points={{-120,-60},{-80,-60},
              {-80,170},{18,170}}, color={0,0,127}));
      connect(cutoff, not1.u) annotation (Line(points={{-120,0},{-60,0},{-60,90},
              {18,90}},                   color={255,0,255}));
      connect(and2.y, transitionWithSignal5.condition) annotation (Line(points={{81,130},
              {104,130},{104,12},{0,12},{0,18}},
            color={255,0,255}));
      connect(and1.y, transitionWithSignal6.condition) annotation (Line(points={{81,190},
              {106,190},{106,6},{70,6},{70,18}},           color={255,0,255}));
      connect(stepWithSignal3.outPort[1], transitionWithSignal6.inPort)
        annotation (Line(points={{40.5,30},{66,30}}, color={0,0,0}));
      connect(transitionWithSignal6.outPort, initialStep.inPort[2]) annotation (
         Line(points={{71.5,30},{102,30},{102,48},{-46,48},{-46,-29.75},{-41,
              -29.75}},   color={0,0,0}));
      connect(initialStep.outPort[2], transitionWithSignal5.inPort) annotation (
         Line(points={{-19.5,-29.875},{-14,-29.875},{-14,30},{-4,30}}, color={0,
              0,0}));
      connect(not1.y, and2.u2) annotation (Line(points={{41,90},{48,90},{48,122},
              {58,122}}, color={255,0,255}));
      connect(or1.y, and2.u1)
        annotation (Line(points={{41,130},{58,130}}, color={255,0,255}));
      connect(hp_active, deadband_res.u) annotation (Line(points={{-120,-30},{-90,
              -30},{-90,-46},{-140,-46},{-140,-130},{-122,-130}}, color={255,0,
              255}));
      connect(stepWithSignal1.active, or2.u[1]) annotation (Line(points={{30,-41},
              {30,-60},{110,-60},{110,-72.3333},{160,-72.3333}},      color={
              255,0,255}));
      connect(stepWithSignal2.active, or2.u[2]) annotation (Line(points={{90,
              -41},{90,-70},{160,-70}}, color={255,0,255}));
      connect(stepWithSignal3.active, or2.u[3]) annotation (Line(points={{30,19},
              {30,0},{72,0},{72,-67.6667},{160,-67.6667}}, color={255,0,255}));
      connect(or2.y, y) annotation (Line(points={{181.5,-70},{190,-70},{190,20},
              {90,20},{90,0},{110,0}}, color={255,0,255}));
      connect(greater3.y, or3.u[1]) annotation (Line(points={{81,-160},{92,-160},
              {92,-141.75},{100,-141.75}}, color={255,0,255}));
      connect(or3.y, transitionWithSignal2.condition) annotation (Line(points={
              {121.5,-140},{130,-140},{130,-42}}, color={255,0,255}));
      connect(greater4.y, or3.u[2]) annotation (Line(points={{83,-130},{92,-130},
              {92,-138.25},{100,-138.25}}, color={255,0,255}));
      connect(TTop, less3.u1) annotation (Line(points={{-120,-60},{-80,-60},{
              -80,-80},{-52,-80},{-52,-120},{-42,-120}}, color={0,0,127}));
      connect(add1.y, less3.u2) annotation (Line(points={{-59,-170},{-52,-170},
              {-52,-128},{-42,-128}}, color={0,0,127}));
      connect(Tset_res, add1.u1) annotation (Line(points={{-120,60},{-82,60},{
              -82,-164}}, color={0,0,127}));
      connect(deadband_res.y, add1.u2) annotation (Line(points={{-99,-130},{-94,
              -130},{-94,-176},{-82,-176}}, color={0,0,127}));
      connect(Tset_hp, greater5.u2) annotation (Line(points={{-120,90},{-98,90},
              {-98,252},{18,252}}, color={0,0,127}));
      connect(TTop, greater5.u1) annotation (Line(points={{-120,-60},{-80,-60},
              {-80,260},{18,260}}, color={0,0,127}));
      connect(initialStep1.outPort[1], transitionWithSignal3.inPort)
        annotation (Line(points={{120.5,270},{136,270}}, color={0,0,0}));
      connect(transitionWithSignal3.outPort, stepWithSignal4.inPort[1])
        annotation (Line(points={{141.5,270},{159,270}}, color={0,0,0}));
      connect(Tset_hp, greater6.u2) annotation (Line(points={{-120,90},{-98,90},
              {-98,222},{18,222}}, color={0,0,127}));
      connect(TBottom, greater6.u1) annotation (Line(points={{-120,-90},{-74,
              -90},{-74,230},{18,230}}, color={0,0,127}));
      connect(stepWithSignal4.outPort[1], transitionWithSignal7.inPort)
        annotation (Line(points={{180.5,270},{196,270}}, color={0,0,0}));
      connect(stepWithSignal3.active, transitionWithSignal3.condition)
        annotation (Line(points={{30,19},{30,6},{60,6},{60,108},{140,108},{140,
              258}}, color={255,0,255}));
      connect(greater5.y, transitionWithSignal7.condition) annotation (Line(
            points={{41,260},{60,260},{60,248},{200,248},{200,258}}, color={255,
              0,255}));
      connect(transitionWithSignal7.outPort, stepWithSignal5.inPort[1])
        annotation (Line(points={{201.5,270},{219,270}}, color={0,0,0}));
      connect(stepWithSignal5.outPort[1], transitionWithSignal8.inPort)
        annotation (Line(points={{240.5,270},{256,270}}, color={0,0,0}));
      connect(transitionWithSignal8.outPort, initialStep1.inPort[1])
        annotation (Line(points={{261.5,270},{270,270},{270,292},{90,292},{90,
              270},{99,270}}, color={0,0,0}));
      connect(greater6.y, transitionWithSignal8.condition) annotation (Line(
            points={{41,230},{260,230},{260,258}}, color={255,0,255}));
      connect(stepWithSignal1.active, or4.u[1]) annotation (Line(points={{30,-41},
              {30,-60},{150,-60},{150,127.667},{178,127.667}},      color={255,
              0,255}));
      connect(stepWithSignal2.active, or4.u[2]) annotation (Line(points={{90,
              -41},{90,-58},{152,-58},{152,130},{178,130}}, color={255,0,255}));
      connect(stepWithSignal4.active, or4.u[3]) annotation (Line(points={{170,259},
              {170,132.333},{178,132.333}},      color={255,0,255}));
      connect(or4.y, and4.u1)
        annotation (Line(points={{199.5,130},{218,130}}, color={255,0,255}));
      connect(or2.y, and4.u2) annotation (Line(points={{181.5,-70},{210,-70},{
              210,122},{218,122}}, color={255,0,255}));
      connect(and4.y, top) annotation (Line(points={{241,130},{250,130},{250,
              100},{92,100},{92,90},{110,90}}, color={255,0,255}));
      connect(stepWithSignal5.active, and5.u1) annotation (Line(points={{230,
              259},{230,190},{238,190}}, color={255,0,255}));
      connect(or2.y, and5.u2) annotation (Line(points={{181.5,-70},{210,-70},{
              210,182},{238,182}}, color={255,0,255}));
      connect(and5.y, bottom) annotation (Line(points={{261,190},{270,190},{270,
              72},{92,72},{92,60},{110,60}}, color={255,0,255}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                                    Rectangle(
            extent={{-100,-100},{100,100}},
            lineColor={0,0,127},
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
            Text(
              extent={{-150,146},{150,106}},
              textColor={0,0,255},
              textString="%name")}), Diagram(coordinateSystem(
              preserveAspectRatio=false)),
        Documentation(info="<html>
<p align=\"center\">
<img alt=\"image\" src=\"modelica://models/Resources/Images/HPWH/rheem_proph80/Controls/resistance.svg\" border=\"0\"/>
</p>
</html>
"));
    end res_state;

    model deadband
      models.Controls.changing_setpoint changing_setpoint1
        annotation (Placement(transformation(extent={{-80,-10},{-60,10}})));
      Modelica.Blocks.Sources.RealExpression realExpression1(y=
            deadband_hp_recent) annotation (Placement(transformation(extent={{20,-10},
                {40,10}})));
      Modelica.Blocks.Sources.RealExpression realExpression2(y=deadband_hp)
        annotation (Placement(transformation(extent={{20,-70},{40,-50}})));
      Modelica.Blocks.Interfaces.RealOutput y
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Interfaces.RealInput Tset_hp(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      parameter Modelica.Blocks.Interfaces.RealOutput deadband_hp_recent=5
        "Value of Real output";
      parameter Modelica.Blocks.Interfaces.RealOutput deadband_hp=5
        "Value of Real output";
      Modelica.StateGraph.InitialStep initialStepWithSignal(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{-90,40},{-70,60}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal(nIn=1, nOut=1)
        annotation (Placement(transformation(extent={{-30,40},{-10,60}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal
        annotation (Placement(transformation(extent={{-60,40},{-40,60}})));
      Modelica.Blocks.Logical.Not not1
        annotation (Placement(transformation(extent={{-30,-10},{-10,10}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal1
        annotation (Placement(transformation(extent={{0,40},{20,60}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal1(nIn=1, nOut=1)
        annotation (Placement(transformation(extent={{30,40},{50,60}})));
      Modelica.StateGraph.Transition           transitionWithSignal2(
          enableTimer=true, waitTime=hp_timewindow)
        annotation (Placement(transformation(extent={{60,40},{80,60}})));
      Modelica.Blocks.Logical.Switch switch1
        annotation (Placement(transformation(extent={{60,-40},{80,-20}})));
      Modelica.Blocks.Logical.Or or1
        annotation (Placement(transformation(extent={{20,-40},{40,-20}})));
      parameter Modelica.Units.SI.Time hp_timewindow=0
        "Wait time before transition fires";
    equation
      connect(Tset_hp, changing_setpoint1.u)
        annotation (Line(points={{-120,0},{-82,0}}, color={0,0,127}));
      connect(initialStepWithSignal.outPort[1], transitionWithSignal.inPort)
        annotation (Line(points={{-69.5,50},{-54,50}}, color={0,0,0}));
      connect(transitionWithSignal.outPort, stepWithSignal.inPort[1])
        annotation (Line(points={{-48.5,50},{-31,50}}, color={0,0,0}));
      connect(stepWithSignal.outPort[1], transitionWithSignal1.inPort)
        annotation (Line(points={{-9.5,50},{6,50}}, color={0,0,0}));
      connect(changing_setpoint1.y, transitionWithSignal.condition) annotation (
         Line(points={{-59,0},{-50,0},{-50,38}}, color={255,0,255}));
      connect(changing_setpoint1.y, not1.u)
        annotation (Line(points={{-59,0},{-32,0}}, color={255,0,255}));
      connect(not1.y, transitionWithSignal1.condition)
        annotation (Line(points={{-9,0},{10,0},{10,38}}, color={255,0,255}));
      connect(transitionWithSignal1.outPort, stepWithSignal1.inPort[1])
        annotation (Line(points={{11.5,50},{29,50}}, color={0,0,0}));
      connect(stepWithSignal1.outPort[1], transitionWithSignal2.inPort)
        annotation (Line(points={{50.5,50},{66,50}}, color={0,0,0}));
      connect(transitionWithSignal2.outPort, initialStepWithSignal.inPort[1])
        annotation (Line(points={{71.5,50},{80,50},{80,80},{-100,80},{-100,50},
              {-91,50}}, color={0,0,0}));
      connect(stepWithSignal.active, or1.u2) annotation (Line(points={{-20,39},
              {-20,24},{0,24},{0,-38},{18,-38}}, color={255,0,255}));
      connect(stepWithSignal1.active, or1.u1) annotation (Line(points={{40,39},
              {40,24},{14,24},{14,-30},{18,-30}}, color={255,0,255}));
      connect(or1.y, switch1.u2)
        annotation (Line(points={{41,-30},{58,-30}}, color={255,0,255}));
      connect(realExpression1.y, switch1.u1) annotation (Line(points={{41,0},{
              50,0},{50,-22},{58,-22}}, color={0,0,127}));
      connect(realExpression2.y, switch1.u3) annotation (Line(points={{41,-60},
              {50,-60},{50,-38},{58,-38}}, color={0,0,127}));
      connect(switch1.y, y) annotation (Line(points={{81,-30},{90,-30},{90,0},{
              110,0}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                                    Rectangle(
            extent={{-100,-100},{100,100}},
            lineColor={0,0,127},
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
            Text(
              extent={{-150,144},{150,104}},
              textColor={0,0,255},
              textString="%name")}), Diagram(coordinateSystem(
              preserveAspectRatio=false)),
        Documentation(info="<html>
<p>The deadband evolves depending on the setpoint temperature. At the time when the setpoint temperature changes, the deadband evolves, going from <i>deadband_hp</i> to <i>deadband_hp_recent</i> for <i>hp_timewindow</i> seconds</p>
<p align=\"center\">
<img alt=\"image\" src=\"modelica://models/Resources/Images/HPWH/rheem_proph80/Controls/deadband.svg\" border=\"0\"/>
</p>
</html>
"));
    end deadband;

    model hp_state_cta
      Modelica.StateGraph.InitialStep initialStep(nOut=4, nIn=1)
        annotation (Placement(transformation(extent={{-80,-10},{-60,10}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal
        annotation (Placement(transformation(extent={{-40,40},{-20,60}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal1
        annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal2
        annotation (Placement(transformation(extent={{-40,-60},{-20,-40}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal(nIn=1, nOut=1)
        annotation (Placement(transformation(extent={{-10,40},{10,60}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal1(nIn=1, nOut=1)
        annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal2(nIn=1, nOut=1)
        annotation (Placement(transformation(extent={{-10,-60},{10,-40}})));
      Modelica.StateGraph.Transition transition1(enableTimer=true, waitTime=
            cycle_time)
        annotation (Placement(transformation(extent={{20,40},{40,60}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal3(nIn=4, nOut=1)
        annotation (Placement(transformation(extent={{60,40},{80,60}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal4(nOut=1, nIn=1)
        annotation (Placement(transformation(extent={{50,-60},{70,-40}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal3
        annotation (Placement(transformation(extent={{90,40},{110,60}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal4
        annotation (Placement(transformation(extent={{80,-60},{100,-40}})));
      parameter Modelica.Units.SI.Time cycle_time=300
        "Wait time before transition fires";
      Modelica.StateGraph.Transition transition2(enableTimer=true, waitTime=
            cycle_time)
        annotation (Placement(transformation(extent={{20,-60},{40,-40}})));
      Modelica.Blocks.Interfaces.RealInput Ttop(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Temperature at the top of the tank"
        annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
      Modelica.Blocks.Interfaces.RealInput Tbottom(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Temperature at the bottom of the tank"
        annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
      Buildings.Controls.OBC.CDL.Interfaces.BooleanInput res
        "Active resistance"
        annotation (Placement(transformation(extent={{-140,-30},{-100,10}})));
      Modelica.Blocks.Logical.Not not1
        annotation (Placement(transformation(extent={{28,-90},{48,-70}})));
      Modelica.Blocks.Interfaces.RealInput Tset_user_hp(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
      Modelica.Blocks.Logical.Or or1
        annotation (Placement(transformation(extent={{60,280},{80,300}})));
      Modelica.Blocks.Logical.GreaterEqual greaterEqualThreshold
        annotation (Placement(transformation(extent={{20,294},{40,314}})));
      Modelica.Blocks.Logical.GreaterEqual greaterEqualThreshold1
        annotation (Placement(transformation(extent={{80,250},{100,270}})));
      Modelica.Blocks.Math.Add add
        annotation (Placement(transformation(extent={{-40,294},{-20,314}})));
      Modelica.Blocks.Sources.RealExpression realExpression(y=1)
        annotation (Placement(transformation(extent={{-80,300},{-60,320}})));
      Modelica.Blocks.Interfaces.BooleanOutput y
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.MathBoolean.Or or2(nu=6)
        annotation (Placement(transformation(extent={{80,-120},{100,-100}})));
      Modelica.Blocks.Logical.LessEqual lessEqual
        annotation (Placement(transformation(extent={{-60,-160},{-40,-140}})));
      Modelica.Blocks.Logical.LessEqual lessEqual1
        annotation (Placement(transformation(extent={{-60,-200},{-40,-180}})));

      Modelica.Blocks.Math.Add add1(k2=-1) annotation (Placement(transformation(
              extent={{-120,-160},{-100,-140}})));
      Modelica.Blocks.Math.Add add2(k2=-1)
        annotation (Placement(transformation(extent={{0,192},{20,212}})));
      Modelica.Blocks.Logical.Less      lessEqual2
        annotation (Placement(transformation(extent={{40,200},{60,220}})));
      Modelica.Blocks.Sources.RealExpression realExpression3(y=
            deadband_low_stratification)
        annotation (Placement(transformation(extent={{-160,112},{-140,132}})));
      parameter Modelica.Blocks.Interfaces.RealOutput
        deadband_low_stratification=5 "Value of Real output";
      Modelica.Blocks.Math.Add add3(k2=-1)
        annotation (Placement(transformation(extent={{0,152},{20,172}})));
      Modelica.Blocks.Logical.LessThreshold
                                        lessThreshold(threshold=5)
        annotation (Placement(transformation(extent={{40,152},{60,172}})));
      Buildings.Controls.OBC.CDL.Interfaces.BooleanInput cutoff
        "Active resistance"
        annotation (Placement(transformation(extent={{-140,-50},{-100,-10}})));
      Modelica.Blocks.Logical.And or5
        annotation (Placement(transformation(extent={{120,-140},{140,-120}})));
      Modelica.Blocks.Interfaces.RealInput deadband
                            "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,10},{-100,50}})));
      Modelica.StateGraph.Transition transition3(enableTimer=true, waitTime=
            cycle_time)
        annotation (Placement(transformation(extent={{20,-10},{40,10}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal5
        annotation (Placement(transformation(extent={{-40,80},{-20,100}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal5(nIn=1, nOut=1)
        annotation (Placement(transformation(extent={{-10,80},{10,100}})));
      Modelica.StateGraph.Transition transition4(enableTimer=true, waitTime=
            cycle_time)
        annotation (Placement(transformation(extent={{20,80},{40,100}})));
      Modelica.Blocks.Interfaces.IntegerInput cta_signal annotation (Placement(
            transformation(
            extent={{-20,-20},{20,20}},
            rotation=270,
            origin={70,120})));
      Modelica.Blocks.MathBoolean.And and1(nu=3)
        annotation (Placement(transformation(extent={{-20,-200},{0,-180}})));
      Modelica.Blocks.Math.IntegerToBoolean integerToBoolean(threshold=1)
        annotation (Placement(transformation(extent={{140,80},{160,100}})));
      Modelica.Blocks.MathBoolean.And and2(nu=3)
        annotation (Placement(transformation(extent={{80,180},{100,200}})));
      Modelica.Blocks.Logical.And and3 annotation (Placement(transformation(
            extent={{-10,-10},{10,10}},
            rotation=90,
            origin={-30,-110})));
      Modelica.Blocks.MathBoolean.And and4(nu=2)
        annotation (Placement(transformation(extent={{190,100},{210,120}})));
      Modelica.Blocks.Logical.Not not3
        annotation (Placement(transformation(extent={{140,250},{160,270}})));
      cta cta1(
        dt_loadup=cta_dt_loadup,
        dt_advanced=cta_dt_advanced,
        dt_shed=cta_dt_shed,
        user_deadband=cta_user_deadband)
        annotation (Placement(transformation(extent={{-120,120},{-100,140}})));
      Modelica.Blocks.Math.IntegerToBoolean integerToBoolean1(threshold=0)
        annotation (Placement(transformation(extent={{140,120},{160,140}})));
      parameter Modelica.Units.SI.Time cta_dt_loadup=0
        "Wait time before transition fires" annotation (Dialog(group="CTA"));
      parameter Modelica.Units.SI.Time cta_dt_advanced=0
        "Wait time before transition fires" annotation (Dialog(group="CTA"));
      parameter Modelica.Units.SI.Time cta_dt_shed=0
        "Wait time before transition fires" annotation (Dialog(group="CTA"));
      parameter Modelica.Blocks.Interfaces.RealOutput cta_user_deadband=2/1.8
        "Value of Real output" annotation (Dialog(group="CTA"));
      Modelica.Blocks.Interfaces.RealInput Tdelta
        "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,70},{-100,110}})));
      Modelica.Blocks.Math.Add add4
        annotation (Placement(transformation(extent={{-80,70},{-60,90}})));
      Modelica.Blocks.Logical.GreaterEqual greaterEqualThreshold2
        annotation (Placement(transformation(extent={{20,262},{40,282}})));
      Modelica.Blocks.Logical.Switch switch1
        annotation (Placement(transformation(extent={{-80,260},{-60,280}})));
    equation
      connect(initialStep.outPort[1], transitionWithSignal1.inPort) annotation (
         Line(points={{-59.5,-0.1875},{-46,-0.1875},{-46,0},{-34,0}},     color
            ={0,0,0}));
      connect(initialStep.outPort[2], transitionWithSignal.inPort) annotation (
          Line(points={{-59.5,-0.0625},{-44,-0.0625},{-44,50},{-34,50}},
                                                             color={0,0,0}));
      connect(initialStep.outPort[3], transitionWithSignal2.inPort) annotation (
         Line(points={{-59.5,0.0625},{-44,0.0625},{-44,-50},{-34,-50}},
            color={0,0,0}));
      connect(transitionWithSignal.outPort, stepWithSignal.inPort[1])
        annotation (Line(points={{-28.5,50},{-11,50}}, color={0,0,0}));
      connect(transitionWithSignal1.outPort, stepWithSignal1.inPort[1])
        annotation (Line(points={{-28.5,0},{-11,0}}, color={0,0,0}));
      connect(transitionWithSignal2.outPort, stepWithSignal2.inPort[1])
        annotation (Line(points={{-28.5,-50},{-11,-50}}, color={0,0,0}));
      connect(stepWithSignal3.outPort[1], transitionWithSignal3.inPort)
        annotation (Line(points={{80.5,50},{96,50}}, color={0,0,0}));
      connect(stepWithSignal4.outPort[1], transitionWithSignal4.inPort)
        annotation (Line(points={{70.5,-50},{86,-50}}, color={0,0,0}));
      connect(transitionWithSignal4.outPort, stepWithSignal3.inPort[1])
        annotation (Line(points={{91.5,-50},{106,-50},{106,-22},{50,-22},{50,
              49.625},{59,49.625}},
                                  color={0,0,0}));
      connect(transitionWithSignal3.outPort, initialStep.inPort[1]) annotation (
         Line(points={{101.5,50},{110,50},{110,70},{-94,70},{-94,0},{-81,0}},
            color={0,0,0}));
      connect(stepWithSignal2.outPort[1], transition2.inPort)
        annotation (Line(points={{10.5,-50},{26,-50}},color={0,0,0}));
      connect(transition2.outPort, stepWithSignal4.inPort[1])
        annotation (Line(points={{31.5,-50},{49,-50}}, color={0,0,0}));
      connect(res, not1.u)
        annotation (Line(points={{-120,-10},{-86,-10},{-86,-80},{26,-80}},
                                                       color={255,0,255}));
      connect(not1.y, transitionWithSignal4.condition) annotation (Line(points=
              {{49,-80},{90,-80},{90,-62}}, color={255,0,255}));
      connect(Tbottom, greaterEqualThreshold1.u1) annotation (Line(points={{-120,
              -100},{-50,-100},{-50,260},{78,260}},              color={0,0,127}));
      connect(realExpression.y, add.u1)
        annotation (Line(points={{-59,310},{-42,310}}, color={0,0,127}));
      connect(add.y, greaterEqualThreshold.u2) annotation (Line(points={{-19,304},
              {-12,304},{-12,296},{18,296}},      color={0,0,127}));
      connect(Ttop, greaterEqualThreshold.u1) annotation (Line(points={{-120,
              -60},{-90,-60},{-90,288},{4,288},{4,304},{18,304}},
                                                            color={0,0,127}));
      connect(greaterEqualThreshold.y, or1.u1) annotation (Line(points={{41,304},
              {50,304},{50,290},{58,290}}, color={255,0,255}));
      connect(or1.y, transitionWithSignal3.condition) annotation (Line(points={{81,290},
              {116,290},{116,28},{100,28},{100,38}},          color={255,0,255}));
      connect(stepWithSignal3.active, or2.u[1]) annotation (Line(points={{70,39},
              {70,-26},{20,-26},{20,-108},{80,-108},{80,-112.917}},
                                                          color={255,0,255}));
      connect(stepWithSignal4.active, or2.u[2]) annotation (Line(points={{60,-61},
              {60,-111.75},{80,-111.75}},    color={255,0,255}));
      connect(stepWithSignal.active, or2.u[3]) annotation (Line(points={{0,39},{
              0,28},{20,28},{20,-110.583},{80,-110.583}},
                                                     color={255,0,255}));
      connect(stepWithSignal1.active, or2.u[4]) annotation (Line(points={{0,-11},
              {0,-20},{20,-20},{20,-109.417},{80,-109.417}},
                                                           color={255,0,255}));
      connect(stepWithSignal2.active, or2.u[5]) annotation (Line(points={{0,-61},
              {0,-108.25},{80,-108.25}},
                                       color={255,0,255}));
      connect(Tbottom, lessEqual.u1) annotation (Line(points={{-120,-100},{-72,
              -100},{-72,-150},{-62,-150}},
                                      color={0,0,127}));
      connect(Ttop, lessEqual1.u1) annotation (Line(points={{-120,-60},{-90,-60},
              {-90,-190},{-62,-190}}, color={0,0,127}));
      connect(add1.y, lessEqual.u2) annotation (Line(points={{-99,-150},{-76,
              -150},{-76,-158},{-62,-158}}, color={0,0,127}));
      connect(add2.y, lessEqual2.u2)
        annotation (Line(points={{21,202},{38,202}}, color={0,0,127}));
      connect(Ttop, lessEqual2.u1) annotation (Line(points={{-120,-60},{-90,-60},
              {-90,220},{30,220},{30,210},{38,210}}, color={0,0,127}));
      connect(add3.y, lessThreshold.u)
        annotation (Line(points={{21,162},{38,162}}, color={0,0,127}));
      connect(Ttop, add3.u1) annotation (Line(points={{-120,-60},{-90,-60},{-90,
              168},{-2,168}}, color={0,0,127}));
      connect(Tbottom, add3.u2) annotation (Line(points={{-120,-100},{-50,-100},
              {-50,156},{-2,156}},color={0,0,127}));
      connect(or2.y, or5.u1) annotation (Line(points={{101.5,-110},{110,-110},{
              110,-130},{118,-130}}, color={255,0,255}));
      connect(cutoff, or5.u2) annotation (Line(points={{-120,-30},{-94,-30},{
              -94,-134},{108,-134},{108,-138},{118,-138}},
                                     color={255,0,255}));
      connect(or5.y, y) annotation (Line(points={{141,-130},{150,-130},{150,-20},
              {90,-20},{90,0},{110,0}}, color={255,0,255}));
      connect(stepWithSignal1.outPort[1], transition3.inPort)
        annotation (Line(points={{10.5,0},{26,0}}, color={0,0,0}));
      connect(stepWithSignal.outPort[1], transition1.inPort)
        annotation (Line(points={{10.5,50},{26,50}}, color={0,0,0}));
      connect(transition1.outPort, stepWithSignal3.inPort[2]) annotation (Line(
            points={{31.5,50},{46,50},{46,49.875},{59,49.875}},
                                                        color={0,0,0}));
      connect(transition3.outPort, stepWithSignal3.inPort[3]) annotation (Line(
            points={{31.5,0},{50,0},{50,50.125},{59,50.125}},
            color={0,0,0}));
      connect(transitionWithSignal5.outPort, stepWithSignal5.inPort[1])
        annotation (Line(points={{-28.5,90},{-11,90}}, color={0,0,0}));
      connect(stepWithSignal5.outPort[1], transition4.inPort)
        annotation (Line(points={{10.5,90},{26,90}}, color={0,0,0}));
      connect(transition4.outPort, stepWithSignal3.inPort[4]) annotation (Line(
            points={{31.5,90},{50,90},{50,50.375},{59,50.375}}, color={0,0,0}));
      connect(initialStep.outPort[4], transitionWithSignal5.inPort) annotation (
         Line(points={{-59.5,0.1875},{-44,0.1875},{-44,90},{-34,90}}, color={0,
              0,0}));
      connect(lessEqual.y, and1.u[1]) annotation (Line(points={{-39,-150},{-30,
              -150},{-30,-192.333},{-20,-192.333}}, color={255,0,255}));
      connect(lessEqual1.y, and1.u[2]) annotation (Line(points={{-39,-190},{-20,
              -190}},            color={255,0,255}));
      connect(and1.y, transitionWithSignal.condition) annotation (Line(points={
              {1.5,-190},{10,-190},{10,-128},{-54,-128},{-54,28},{-30,28},{-30,
              38}}, color={255,0,255}));
      connect(lessThreshold.y, and2.u[1]) annotation (Line(points={{61,162},{68,
              162},{68,187.667},{80,187.667}}, color={255,0,255}));
      connect(lessEqual2.y, and2.u[2]) annotation (Line(points={{61,210},{68,210},{68,
              190},{80,190}},          color={255,0,255}));
      connect(cta_signal, integerToBoolean.u) annotation (Line(points={{70,120},{70,
              90},{138,90}},     color={255,127,0}));
      connect(res, and3.u2) annotation (Line(points={{-120,-10},{-86,-10},{-86,
              -80},{-14,-80},{-14,-126},{-22,-126},{-22,-122}}, color={255,0,
              255}));
      connect(and3.y, transitionWithSignal2.condition) annotation (Line(points=
              {{-30,-99},{-30,-62},{-30,-62}}, color={255,0,255}));
      connect(and2.y, transitionWithSignal1.condition) annotation (Line(points={{101.5,
              190},{120,190},{120,-28},{-30,-28},{-30,-12}},         color={255,
              0,255}));
      connect(greaterEqualThreshold1.y, not3.u)
        annotation (Line(points={{101,260},{138,260}},color={255,0,255}));
      connect(not3.y, and4.u[1]) annotation (Line(points={{161,260},{184,260},{
              184,108.25},{190,108.25}},   color={255,0,255}));
      connect(and4.y, transitionWithSignal5.condition) annotation (Line(points={{211.5,
              110},{216,110},{216,72},{-30,72},{-30,78}},         color={255,0,
              255}));
      connect(cta_signal, cta1.cta_signal) annotation (Line(points={{70,120},{
              70,90},{90,90},{90,146},{-128,146},{-128,138},{-122,138}},
                                                         color={255,127,0}));
      connect(realExpression3.y, cta1.dband_low_strat)
        annotation (Line(points={{-139,122},{-122,122}}, color={0,0,127}));
      connect(deadband, cta1.deadband) annotation (Line(points={{-120,30},{-166,
              30},{-166,138},{-130,138},{-130,126},{-122,126}},
                                                             color={0,0,127}));
      connect(cta1.dband_low_strat_out, add2.u2) annotation (Line(points={{-99,
              121},{-20,121},{-20,196},{-2,196}}, color={0,0,127}));
      connect(Tset_user_hp, cta1.Tset_hp) annotation (Line(points={{-120,60},{-132,
              60},{-132,130},{-122,130}}, color={0,0,127}));
      connect(cta1.deadband_out, add1.u2) annotation (Line(points={{-99,124},{
              -94,124},{-94,112},{-140,112},{-140,-156},{-122,-156}}, color={0,
              0,127}));
      connect(cta1.Tset_cta, greaterEqualThreshold1.u2) annotation (Line(points
            ={{-99,127},{-94,127},{-94,252},{78,252}}, color={0,0,127}));
      connect(integerToBoolean.y, and4.u[2]) annotation (Line(points={{161,90},
              {174,90},{174,112},{182,112},{182,111.75},{190,111.75}},
                                              color={255,0,255}));
      connect(cta_signal, integerToBoolean1.u) annotation (Line(points={{70,120},
              {70,90},{130,90},{130,130},{138,130}},
                                                 color={255,127,0}));
      connect(integerToBoolean1.y, and2.u[3]) annotation (Line(points={{161,130},
              {170,130},{170,170},{74,170},{74,192.333},{80,192.333}},
                                                                  color={255,0,255}));
      connect(integerToBoolean1.y, and1.u[3]) annotation (Line(points={{161,130},
              {170,130},{170,-174},{-26,-174},{-26,-187.667},{-20,-187.667}},
                                                                         color={255,
              0,255}));
      connect(integerToBoolean1.y, and3.u1) annotation (Line(points={{161,130},
              {170,130},{170,-142},{-30,-142},{-30,-122}}, color={255,0,255}));
      connect(stepWithSignal5.active, or2.u[6]) annotation (Line(points={{0,79},{
              0,76},{20,76},{20,-107.083},{80,-107.083}},  color={255,0,255}));
      connect(Tset_user_hp, add4.u2) annotation (Line(points={{-120,60},{-96,60},
              {-96,74},{-82,74}}, color={0,0,127}));
      connect(Tdelta, add4.u1) annotation (Line(points={{-120,90},{-96,90},{-96,
              86},{-82,86}}, color={0,0,127}));
      connect(greaterEqualThreshold2.y, or1.u2) annotation (Line(points={{41,
              272},{50,272},{50,282},{58,282}}, color={255,0,255}));
      connect(Tbottom, greaterEqualThreshold2.u1) annotation (Line(points={{
              -120,-100},{-50,-100},{-50,272},{18,272}}, color={0,0,127}));
      connect(switch1.y, add.u2) annotation (Line(points={{-59,270},{-54,270},{
              -54,298},{-42,298}}, color={0,0,127}));
      connect(switch1.y, greaterEqualThreshold2.u2) annotation (Line(points={{
              -59,270},{-54,270},{-54,264},{18,264}}, color={0,0,127}));
      connect(add4.y, switch1.u3) annotation (Line(points={{-59,80},{-54,80},{
              -54,240},{-100,240},{-100,262},{-82,262}}, color={0,0,127}));
      connect(cta1.Tset_cta, switch1.u1) annotation (Line(points={{-99,127},{
              -94,127},{-94,278},{-82,278}}, color={0,0,127}));
      connect(integerToBoolean.y, switch1.u2) annotation (Line(points={{161,90},
              {174,90},{174,246},{-106,246},{-106,270},{-82,270}}, color={255,0,
              255}));
      connect(add4.y, add2.u1) annotation (Line(points={{-59,80},{-54,80},{-54,
              208},{-2,208}}, color={0,0,127}));
      connect(add4.y, add1.u1) annotation (Line(points={{-59,80},{-54,80},{-54,
              108},{-148,108},{-148,-144},{-122,-144}}, color={0,0,127}));
      connect(add4.y, lessEqual1.u2) annotation (Line(points={{-59,80},{-54,80},
              {-54,108},{-148,108},{-148,-198},{-62,-198}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                                    Rectangle(
            extent={{-100,-100},{100,100}},
            lineColor={0,0,127},
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
            Text(
              extent={{-170,144},{130,104}},
              textColor={0,0,255},
              textString="%name")}),                                 Diagram(
            coordinateSystem(preserveAspectRatio=false)),
        Documentation(info="<html>
<p align=\"center\">
<img alt=\"image\" src=\"modelica://models/Resources/Images/HPWH/rheem_proph80/Controls/HP_cta.svg\" border=\"0\"/>
</p>
</html>"));
    end hp_state_cta;

    model cta
      Modelica.Blocks.Interfaces.IntegerInput cta_signal annotation (Placement(
            transformation(
            extent={{-20,-20},{20,20}},
            rotation=0,
            origin={-120,80})));
      Modelica.Blocks.Interfaces.RealInput Tset_hp(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC") "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealInput deadband
        "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.StateGraph.InitialStepWithSignal
                                      initialStepWithSignal(nOut=3, nIn=3)
        annotation (Placement(transformation(extent={{-80,40},{-60,60}})));
      Modelica.StateGraph.TransitionWithSignal loadup_start
        annotation (Placement(transformation(extent={{-40,80},{-20,100}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal(nIn=3, nOut=1)
        annotation (Placement(transformation(extent={{-10,80},{10,100}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal1
        annotation (Placement(transformation(extent={{20,80},{40,100}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal1(nIn=1, nOut=3)
        annotation (Placement(transformation(extent={{50,80},{70,100}})));
      Modelica.StateGraph.Transition loadup_stop(enableTimer=true, waitTime=
            dt_loadup)
        annotation (Placement(transformation(extent={{80,80},{100,100}})));
      Modelica.StateGraph.TransitionWithSignal advanced_start
        annotation (Placement(transformation(extent={{-40,40},{-20,60}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal2(nIn=3, nOut=1)
        annotation (Placement(transformation(extent={{-10,40},{10,60}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal4
        annotation (Placement(transformation(extent={{20,40},{40,60}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal3(nIn=1, nOut=3)
        annotation (Placement(transformation(extent={{50,40},{70,60}})));
      Modelica.StateGraph.Transition advanced_stop(enableTimer=true, waitTime=
            dt_advanced)
        annotation (Placement(transformation(extent={{80,40},{100,60}})));
      Modelica.StateGraph.TransitionWithSignal shed_start
        annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal4(nIn=3, nOut=1)
        annotation (Placement(transformation(extent={{-10,0},{10,20}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal7
        annotation (Placement(transformation(extent={{20,0},{40,20}})));
      Modelica.StateGraph.StepWithSignal stepWithSignal5(nIn=1, nOut=3)
        annotation (Placement(transformation(extent={{50,0},{70,20}})));
      Modelica.StateGraph.Transition shed_stop(enableTimer=true, waitTime=
            dt_shed)
        annotation (Placement(transformation(extent={{80,0},{100,20}})));
      parameter Modelica.Units.SI.Time dt_loadup=0
        "Wait time before transition fires";
      parameter Modelica.Units.SI.Time dt_advanced=0
        "Wait time before transition fires";
      parameter Modelica.Units.SI.Time dt_shed=0
        "Wait time before transition fires";
      models.Controls.EqualInteger loadup_on(t=1)
        annotation (Placement(transformation(extent={{-80,180},{-60,200}})));
      models.Controls.EqualInteger advanced_on(t=2)
        annotation (Placement(transformation(extent={{-80,150},{-60,170}})));
      models.Controls.EqualInteger shed_on(t=-1)
        annotation (Placement(transformation(extent={{-80,120},{-60,140}})));
      models.Controls.Switch_onoff switch4
        annotation (Placement(transformation(extent={{40,-40},{60,-20}})));
      models.Controls.Switch_onoff switch5
        annotation (Placement(transformation(extent={{40,-70},{60,-50}})));
      models.Controls.Switch_onoff switch6
        annotation (Placement(transformation(extent={{40,-100},{60,-80}})));
      Modelica.Blocks.Logical.Or or1
        annotation (Placement(transformation(extent={{-40,-40},{-20,-20}})));
      Modelica.Blocks.Logical.Or or2
        annotation (Placement(transformation(extent={{-40,-70},{-20,-50}})));
      Modelica.Blocks.Logical.Or or3
        annotation (Placement(transformation(extent={{-40,-122},{-20,-102}})));

      Modelica.Blocks.Sources.RealExpression realExpression3(y=user_deadband)
        annotation (Placement(transformation(extent={{6,-32},{26,-12}})));
      Modelica.Blocks.Sources.RealExpression realExpression4(y=user_deadband)
        annotation (Placement(transformation(extent={{6,-62},{26,-42}})));
      Modelica.Blocks.Interfaces.RealInput dband_low_strat
        "Setpoint temperature for the HP"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
      parameter Modelica.Blocks.Interfaces.RealOutput user_deadband=2/1.8
        "Value of Real output";
      Modelica.Blocks.Math.Gain gain(k=1.5)
        annotation (Placement(transformation(extent={{0,-92},{20,-72}})));
      Modelica.Blocks.Logical.Switch switch8
        annotation (Placement(transformation(extent={{80,-160},{100,-140}})));
      Modelica.Blocks.Math.MinMax minMax1(nu=3)
        annotation (Placement(transformation(extent={{40,-126},{60,-106}})));
      Modelica.Blocks.Logical.Switch switch10
        annotation (Placement(transformation(extent={{120,-120},{140,-100}})));
      Modelica.Blocks.Math.Gain gain1(k=1.5)
        annotation (Placement(transformation(extent={{80,-112},{100,-92}})));
      Modelica.Blocks.Interfaces.RealOutput Tset_cta(
        final quantity="ThermodynamicTemperature",
        final unit="K",
        displayUnit="degC")
        annotation (Placement(transformation(extent={{100,-40},{120,-20}})));
      Modelica.Blocks.Interfaces.RealOutput deadband_out
        annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
      Modelica.Blocks.Interfaces.RealOutput dband_low_strat_out
        annotation (Placement(transformation(extent={{100,-100},{120,-80}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal9
        annotation (Placement(transformation(extent={{40,160},{60,180}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal10
        annotation (Placement(transformation(extent={{40,120},{60,140}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal11
        annotation (Placement(transformation(extent={{120,160},{140,180}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal12
        annotation (Placement(transformation(extent={{120,120},{140,140}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal13
        annotation (Placement(transformation(extent={{160,40},{180,60}})));
      Modelica.StateGraph.TransitionWithSignal transitionWithSignal14
        annotation (Placement(transformation(extent={{160,80},{180,100}})));
      Modelica.Blocks.Logical.Switch switch1
        annotation (Placement(transformation(extent={{-40,-180},{-20,-160}})));
      Modelica.Blocks.Sources.RealExpression realExpression(y=15/1.8)
        annotation (Placement(transformation(extent={{-160,-178},{-140,-158}})));
      Modelica.Blocks.Math.Add add
        annotation (Placement(transformation(extent={{-120,-172},{-100,-152}})));
      models.Controls.changing_memory changing_memory1
        annotation (Placement(transformation(extent={{-10,120},{10,140}})));
    equation
      connect(loadup_start.outPort, stepWithSignal.inPort[1]) annotation (Line(
            points={{-28.5,90},{-20,90},{-20,89.6667},{-11,89.6667}}, color={0,
              0,0}));
      connect(stepWithSignal.outPort[1], transitionWithSignal1.inPort)
        annotation (Line(points={{10.5,90},{18,90},{18,90},{26,90}},
                                                     color={0,0,0}));
      connect(transitionWithSignal1.outPort, stepWithSignal1.inPort[1])
        annotation (Line(points={{31.5,90},{49,90}}, color={0,0,0}));
      connect(stepWithSignal1.outPort[1], loadup_stop.inPort) annotation (Line(
            points={{70.5,89.8333},{78,89.8333},{78,90},{86,90}}, color={0,0,0}));
      connect(advanced_start.outPort, stepWithSignal2.inPort[1]) annotation (
          Line(points={{-28.5,50},{-20,50},{-20,49.6667},{-11,49.6667}}, color=
              {0,0,0}));
      connect(stepWithSignal2.outPort[1], transitionWithSignal4.inPort)
        annotation (Line(points={{10.5,50},{18,50},{18,50},{26,50}},
                                                     color={0,0,0}));
      connect(transitionWithSignal4.outPort, stepWithSignal3.inPort[1])
        annotation (Line(points={{31.5,50},{49,50}}, color={0,0,0}));
      connect(stepWithSignal3.outPort[1], advanced_stop.inPort) annotation (
          Line(points={{70.5,49.8333},{78,49.8333},{78,50},{86,50}}, color={0,0,
              0}));
      connect(shed_start.outPort, stepWithSignal4.inPort[1]) annotation (Line(
            points={{-28.5,10},{-20,10},{-20,9.66667},{-11,9.66667}}, color={0,
              0,0}));
      connect(stepWithSignal4.outPort[1], transitionWithSignal7.inPort)
        annotation (Line(points={{10.5,10},{18,10},{18,10},{26,10}},
                                                     color={0,0,0}));
      connect(transitionWithSignal7.outPort, stepWithSignal5.inPort[1])
        annotation (Line(points={{31.5,10},{49,10}}, color={0,0,0}));
      connect(stepWithSignal5.outPort[1], shed_stop.inPort) annotation (Line(
            points={{70.5,9.83333},{78,9.83333},{78,10},{86,10}}, color={0,0,0}));
      connect(initialStepWithSignal.outPort[1], advanced_start.inPort)
        annotation (Line(points={{-59.5,49.8333},{-46,49.8333},{-46,50},{-34,50}},
            color={0,0,0}));
      connect(initialStepWithSignal.outPort[2], loadup_start.inPort)
        annotation (Line(points={{-59.5,50},{-48,50},{-48,90},{-34,90}}, color=
              {0,0,0}));
      connect(initialStepWithSignal.outPort[3], shed_start.inPort) annotation (
          Line(points={{-59.5,50.1667},{-48,50.1667},{-48,10},{-34,10}}, color=
              {0,0,0}));
      connect(loadup_stop.outPort, initialStepWithSignal.inPort[1]) annotation (
         Line(points={{91.5,90},{110,90},{110,112},{-90,112},{-90,49.6667},{-81,
              49.6667}}, color={0,0,0}));
      connect(initialStepWithSignal.inPort[2], advanced_stop.outPort)
        annotation (Line(points={{-81,50},{-90,50},{-90,112},{110,112},{110,50},
              {91.5,50}}, color={0,0,0}));
      connect(shed_stop.outPort, initialStepWithSignal.inPort[3]) annotation (
          Line(points={{91.5,10},{110,10},{110,112},{-90,112},{-90,50.3333},{
              -81,50.3333}}, color={0,0,0}));
      connect(advanced_on.y, advanced_start.condition) annotation (Line(points=
              {{-58,160},{-44,160},{-44,28},{-30,28},{-30,38}}, color={255,0,
              255}));
      connect(shed_on.y, shed_start.condition) annotation (Line(points={{-58,
              130},{-50,130},{-50,-12},{-30,-12},{-30,-2}}, color={255,0,255}));
      connect(loadup_on.y, loadup_start.condition) annotation (Line(points={{-58,
              190},{-40,190},{-40,68},{-30,68},{-30,78}}, color={255,0,255}));
      connect(cta_signal, loadup_on.u) annotation (Line(points={{-120,80},{-94,
              80},{-94,190},{-82,190}}, color={255,127,0}));
      connect(cta_signal, advanced_on.u) annotation (Line(points={{-120,80},{-94,
              80},{-94,160},{-82,160}}, color={255,127,0}));
      connect(cta_signal, shed_on.u) annotation (Line(points={{-120,80},{-94,80},
              {-94,130},{-82,130}}, color={255,127,0}));
      connect(or1.y, switch4.u2) annotation (Line(points={{-19,-30},{-14,-30},{-14,-10},
              {-48,-10},{-48,8},{-46,8},{-46,30},{112,30},{112,-6},{38,-6},{38,-30}},
                                 color={255,0,255}));
      connect(or2.y, switch5.u2) annotation (Line(points={{-19,-60},{38,-60}},
                                 color={255,0,255}));
      connect(or3.y, switch6.u2) annotation (Line(points={{-19,-112},{30,-112},{30,-90},
              {38,-90}},          color={255,0,255}));
      connect(stepWithSignal.active, or1.u1) annotation (Line(points={{0,79},{0,70},
              {-28,70},{-28,66},{-52,66},{-52,-30},{-42,-30}},       color={255,
              0,255}));
      connect(stepWithSignal1.active, or1.u2) annotation (Line(points={{60,79},{60,74},
              {106,74},{106,106},{-52,106},{-52,68},{-54,68},{-54,-38},{-42,-38}},
                               color={255,0,255}));
      connect(stepWithSignal2.active, or2.u1) annotation (Line(points={{0,39},{0,26},
              {-88,26},{-88,-60},{-42,-60}},       color={255,0,255}));
      connect(stepWithSignal3.active, or2.u2) annotation (Line(points={{60,39},{60,32},
              {114,32},{114,-8},{178,-8},{178,-128},{-86,-128},{-86,-68},{-42,-68}},
                               color={255,0,255}));
      connect(stepWithSignal4.active, or3.u1) annotation (Line(points={{0,-1},{0,-58},
              {-10,-58},{-10,-94},{-50,-94},{-50,-112},{-42,-112}},
                                                     color={255,0,255}));
      connect(stepWithSignal5.active, or3.u2) annotation (Line(points={{60,-1},{60,-14},
              {70,-14},{70,-100},{68,-100},{68,-136},{28,-136},{28,-130},{-50,-130},
              {-50,-120},{-42,-120}},                      color={255,0,255}));
      connect(realExpression3.y, switch4.u1)
        annotation (Line(points={{27,-22},{38,-22}}, color={0,0,127}));
      connect(realExpression4.y, switch5.u1)
        annotation (Line(points={{27,-52},{38,-52}}, color={0,0,127}));
      connect(deadband, gain.u) annotation (Line(points={{-120,-40},{-96,-40},{
              -96,-102},{-8,-102},{-8,-82},{-2,-82}}, color={0,0,127}));
      connect(gain.y, switch6.u1)
        annotation (Line(points={{21,-82},{38,-82}}, color={0,0,127}));
      connect(switch4.y, minMax1.u[1]) annotation (Line(points={{61,-30},{66,
              -30},{66,-134},{32,-134},{32,-118.333},{40,-118.333}}, color={0,0,
              127}));
      connect(switch5.y, minMax1.u[2]) annotation (Line(points={{61,-60},{66,
              -60},{66,-134},{32,-134},{32,-116},{40,-116}}, color={0,0,127}));
      connect(switch6.y, minMax1.u[3]) annotation (Line(points={{61,-90},{66,
              -90},{66,-134},{32,-134},{32,-113.667},{40,-113.667}}, color={0,0,
              127}));
      connect(initialStepWithSignal.active, switch8.u2) annotation (Line(points={{-70,39},
              {-70,32},{-92,32},{-92,-150},{78,-150}},
                      color={255,0,255}));
      connect(switch10.u1, gain1.y)
        annotation (Line(points={{118,-102},{101,-102}}, color={0,0,127}));
      connect(or3.y, switch10.u2) annotation (Line(points={{-19,-112},{30,-112},
              {30,-164},{110,-164},{110,-110},{118,-110}},
            color={255,0,255}));
      connect(dband_low_strat, gain1.u) annotation (Line(points={{-120,-80},{
              -98,-80},{-98,-140},{70,-140},{70,-102},{78,-102}},
                                                         color={0,0,127}));
      connect(switch10.y, dband_low_strat_out) annotation (Line(points={{141,
              -110},{150,-110},{150,-80},{94,-80},{94,-90},{110,-90}}, color={0,
              0,127}));
      connect(switch8.y, deadband_out) annotation (Line(points={{101,-150},{160,
              -150},{160,-72},{90,-72},{90,-60},{110,-60}}, color={0,0,127}));
      connect(dband_low_strat, switch10.u3) annotation (Line(points={{-120,-80},
              {-98,-80},{-98,-140},{70,-140},{70,-118},{118,-118}},
                                                           color={0,0,127}));
      connect(transitionWithSignal9.outPort, stepWithSignal2.inPort[2]) annotation (
         Line(points={{51.5,170},{60,170},{60,152},{-22,152},{-22,50},{-11,50}},
            color={0,0,0}));
      connect(transitionWithSignal10.outPort, stepWithSignal4.inPort[2])
        annotation (Line(points={{51.5,130},{60,130},{60,114},{-20,114},{-20,10},{-11,
              10}}, color={0,0,0}));
      connect(stepWithSignal1.outPort[2], transitionWithSignal9.inPort) annotation (
         Line(points={{70.5,90},{80,90},{80,186},{40,186},{40,170},{46,170}}, color
            ={0,0,0}));
      connect(stepWithSignal1.outPort[3], transitionWithSignal10.inPort)
        annotation (Line(points={{70.5,90.1667},{80,90.1667},{80,146},{34,146},
              {34,130},{46,130}},
                         color={0,0,0}));
      connect(stepWithSignal3.outPort[2], transitionWithSignal11.inPort)
        annotation (Line(points={{70.5,50},{74,50},{74,66},{114,66},{114,170},{126,170}},
            color={0,0,0}));
      connect(stepWithSignal3.outPort[3], transitionWithSignal12.inPort)
        annotation (Line(points={{70.5,50.1667},{74,50.1667},{74,66},{114,66},{
              114,130},{126,130}},
                          color={0,0,0}));
      connect(transitionWithSignal11.outPort, stepWithSignal.inPort[2]) annotation (
         Line(points={{131.5,170},{136,170},{136,192},{-16,192},{-16,90},{-11,90}},
            color={0,0,0}));
      connect(transitionWithSignal12.outPort, stepWithSignal4.inPort[3])
        annotation (Line(points={{131.5,130},{140,130},{140,28},{-20,28},{-20,
              10.3333},{-11,10.3333}},
                              color={0,0,0}));
      connect(stepWithSignal5.outPort[2], transitionWithSignal14.inPort)
        annotation (Line(points={{70.5,10},{74,10},{74,24},{148,24},{148,90},{166,90}},
            color={0,0,0}));
      connect(stepWithSignal5.outPort[3], transitionWithSignal13.inPort)
        annotation (Line(points={{70.5,10.1667},{74,10.1667},{74,24},{148,24},{
              148,50},{166,50}},
                         color={0,0,0}));
      connect(transitionWithSignal14.outPort, stepWithSignal.inPort[3]) annotation (
         Line(points={{171.5,90},{180,90},{180,116},{-16,116},{-16,90},{-11,90},
              {-11,90.3333}},
                         color={0,0,0}));
      connect(transitionWithSignal13.outPort, stepWithSignal2.inPort[3])
        annotation (Line(points={{171.5,50},{180,50},{180,68},{-22,68},{-22,
              50.3333},{-11,50.3333}},
                              color={0,0,0}));
      connect(realExpression.y, add.u2)
        annotation (Line(points={{-139,-168},{-122,-168}}, color={0,0,127}));
      connect(or2.y, switch1.u2) annotation (Line(points={{-19,-60},{-14,-60},{-14,-80},
              {-56,-80},{-56,-170},{-42,-170}}, color={255,0,255}));
      connect(add.y, switch1.u1)
        annotation (Line(points={{-99,-162},{-42,-162}}, color={0,0,127}));
      connect(Tset_hp, add.u1) annotation (Line(points={{-120,0},{-130,0},{-130,-156},
              {-122,-156}}, color={0,0,127}));
      connect(Tset_hp, switch1.u3) annotation (Line(points={{-120,0},{-130,0},{-130,
              -178},{-42,-178}}, color={0,0,127}));
      connect(switch1.y, Tset_cta) annotation (Line(points={{-19,-170},{166,-170},
              {166,-40},{88,-40},{88,-30},{110,-30}}, color={0,0,127}));
      connect(minMax1.yMax, switch8.u3) annotation (Line(points={{61,-110},{64,
              -110},{64,-158},{78,-158}}, color={0,0,127}));
      connect(switch8.u1, deadband) annotation (Line(points={{78,-142},{-96,
              -142},{-96,-40},{-120,-40}}, color={0,0,127}));
      connect(cta_signal, changing_memory1.u) annotation (Line(points={{-120,80},
              {-60,80},{-60,116},{-30,116},{-30,130},{-12,130}}, color={255,127,
              0}));
      connect(changing_memory1.y, transitionWithSignal1.condition) annotation (
          Line(points={{11,121},{20,121},{20,72},{30,72},{30,78}}, color={255,0,
              255}));
      connect(changing_memory1.y, transitionWithSignal4.condition) annotation (
          Line(points={{11,121},{20,121},{20,32},{30,32},{30,38}}, color={255,0,
              255}));
      connect(changing_memory1.y, transitionWithSignal7.condition) annotation (
          Line(points={{11,121},{20,121},{20,-8},{30,-8},{30,-2}}, color={255,0,
              255}));
      connect(changing_memory1.y_2, transitionWithSignal9.condition)
        annotation (Line(points={{11,131},{16,131},{16,148},{50,148},{50,158}},
            color={255,0,255}));
      connect(changing_memory1.y_2, transitionWithSignal13.condition)
        annotation (Line(points={{11,131},{16,131},{16,148},{190,148},{190,32},
              {170,32},{170,38}}, color={255,0,255}));
      connect(changing_memory1.y_1, transitionWithSignal11.condition)
        annotation (Line(points={{11,135},{28,135},{28,150},{130,150},{130,158}},
            color={255,0,255}));
      connect(changing_memory1.y_1, transitionWithSignal14.condition)
        annotation (Line(points={{11,135},{28,135},{28,150},{184,150},{184,72},
              {170,72},{170,78}}, color={255,0,255}));
      connect(changing_memory1.y__1, transitionWithSignal10.condition)
        annotation (Line(points={{11,139},{24,139},{24,110},{50,110},{50,118}},
            color={255,0,255}));
      connect(changing_memory1.y__1, transitionWithSignal12.condition)
        annotation (Line(points={{11,139},{24,139},{24,110},{130,110},{130,118}},
            color={255,0,255}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                                    Rectangle(
            extent={{-100,-100},{100,100}},
            lineColor={0,0,127},
            fillColor={255,255,255},
            fillPattern=FillPattern.Solid),
            Text(
              extent={{-170,144},{130,104}},
              textColor={0,0,255},
              textString="%name")}), Diagram(coordinateSystem(
              preserveAspectRatio=false)),
        Documentation(info="<html>
<p>CTA module, the input signals are as follows:</p>
<ul>
<li>Load-up = 1</li>
<li>Advanced = 2</li>
<li>Shed = -1</li>
<li>False = 0</li>
</ul>
<p align=\"center\"><img src=\"modelica://models/Resources/Images/HPWH/rheem_proph80/Controls/cta.svg\" alt=\"image\"/> </p>
</html>"));
    end cta;

  end model_a;
annotation (
Icon(coordinateSystem(preserveAspectRatio=true, extent={{-100.0,-100.0},{100.0,100.0}}), graphics={
      Rectangle(
        origin={0.0,35.1488},
        fillColor={255,255,255},
        extent={{-30.0,-20.1488},{30.0,20.1488}}),
      Rectangle(
        origin={0.0,-34.8512},
        fillColor={255,255,255},
        extent={{-30.0,-20.1488},{30.0,20.1488}}),
      Line(
        origin={-51.25,0.0},
        points={{21.25,-35.0},{-13.75,-35.0},{-13.75,35.0},{6.25,35.0}}),
      Polygon(
        origin={-40.0,35.0},
        pattern=LinePattern.None,
        fillPattern=FillPattern.Solid,
        points={{10.0,0.0},{-5.0,5.0},{-5.0,-5.0}}),
      Line(
        origin={51.25,0.0},
        points={{-21.25,35.0},{13.75,35.0},{13.75,-35.0},{-6.25,-35.0}}),
      Polygon(
        origin={40.0,-35.0},
        pattern=LinePattern.None,
        fillPattern=FillPattern.Solid,
        points={{-10.0,0.0},{5.0,5.0},{5.0,-5.0}})}));
end Controls;
