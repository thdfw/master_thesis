within models.HPWH_MPC;
model plant_hp_fixed
  extends BaseClasses.Partialplant;
  Controls.Switch_onoff switch1
    annotation (Placement(transformation(extent={{-80,100},{-60,120}})));
  Modelica.Blocks.Sources.RealExpression hp_m_flow(y=0.5)
    annotation (Placement(transformation(extent={{-120,120},{-100,140}})));
equation
  connect(greaterThreshold.y, switch1.u2) annotation (Line(points={{-99,96},{
          -92,96},{-92,110},{-82,110}}, color={255,0,255}));
  connect(switch1.y, pump_hp.m_flow_in)
    annotation (Line(points={{-59,110},{-50,110},{-50,92}}, color={0,0,127}));
  connect(hp_m_flow.y, switch1.u1) annotation (Line(points={{-99,130},{-92,130},
          {-92,118},{-82,118}}, color={0,0,127}));
end plant_hp_fixed;
