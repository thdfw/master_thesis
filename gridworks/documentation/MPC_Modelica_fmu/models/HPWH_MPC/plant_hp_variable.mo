within models.HPWH_MPC;
model plant_hp_variable
  extends BaseClasses.Partialplant;
  Equipment.hp_lg hp_lg1
    annotation (Placement(transformation(extent={{-80,100},{-60,120}})));
  Modelica.Blocks.Math.UnitConversions.To_degC to_degC annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=180,
        origin={-110,126})));
equation
  connect(to_degC.y,hp_lg1. TSet) annotation (Line(points={{-99,126},{-92,126},
          {-92,116},{-82,116}}, color={0,0,127}));
  connect(hp_T,to_degC. u) annotation (Line(points={{-120,-30},{-92,-30},{-92,
          80},{-132,80},{-132,126},{-122,126}},   color={0,0,127}));
  connect(hp_lg1.mHP_flow, pump_hp.m_flow_in)
    annotation (Line(points={{-59,110},{-50,110},{-50,92}}, color={0,0,127}));
  connect(greaterThreshold.y, hp_lg1.IO) annotation (Line(points={{-99,96},{-92,
          96},{-92,104},{-82,104}}, color={255,0,255}));
end plant_hp_variable;
