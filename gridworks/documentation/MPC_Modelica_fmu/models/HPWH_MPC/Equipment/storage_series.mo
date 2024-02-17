within models.HPWH_MPC.Equipment;
model storage_series
  extends Buildings.Fluid.Interfaces.PartialTwoPort;
  Buildings.Fluid.Storage.StratifiedEnhanced tan(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal=0.5,
    VTan=VTan,
    hTan=hTan,
    dIns=dIns,
    kIns=kIns,
    nSeg=4,
    T_start=T_start)
    annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
  parameter Modelica.Units.SI.Volume VTan "Tank volume";
  parameter Modelica.Units.SI.Length hTan "Height of tank (without insulation)";
  parameter Modelica.Units.SI.Length dIns "Thickness of insulation";
  parameter Modelica.Units.SI.ThermalConductivity kIns=0.04
    "Specific heat conductivity of insulation";
  parameter Integer nSeg=4 "Number of volume segments";
  Buildings.Fluid.Storage.StratifiedEnhanced tan1(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal=0.5,
    VTan=VTan,
    hTan=hTan,
    dIns=dIns,
    kIns=kIns,
    nSeg=4,
    T_start=T_start)
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
  Buildings.Fluid.Storage.StratifiedEnhanced tan2(
    redeclare package Medium = Buildings.Media.Water,
    m_flow_nominal=0.5,
    VTan=VTan,
    hTan=hTan,
    dIns=dIns,
    kIns=kIns,
    nSeg=4,
    T_start=T_start)
    annotation (Placement(transformation(extent={{20,-10},{40,10}})));
  parameter Modelica.Media.Interfaces.Types.Temperature T_start=60 +273.15
    "Start value of temperature";
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor T_S1[4]
    "Temperature of water in the tank"
    annotation (Placement(transformation(extent={{40,80},{60,100}})));
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor T_S2[4]
    "Temperature of water in the tank"
    annotation (Placement(transformation(extent={{40,50},{60,70}})));
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor T_S3[4]
    "Temperature of water in the tank"
    annotation (Placement(transformation(extent={{40,20},{60,40}})));
  Modelica.Blocks.Interfaces.RealOutput T[12]
    annotation (Placement(transformation(extent={{100,80},{120,100}})));
equation
  for i in 1:4 loop
    connect(T_S1[i].T, T[i]);
    connect(T_S2[i].T, T[4 + i]);
    connect(T_S3[i].T, T[8 + i]);
  end for;

  connect(port_a, tan.port_a) annotation (Line(points={{-100,0},{-80,0},{-80,10},
          {-30,10}}, color={0,127,255}));
  connect(tan.port_b, tan1.port_a) annotation (Line(points={{-30,-10},{-12,-10},
          {-12,10},{0,10}}, color={0,127,255}));
  connect(tan1.port_b, tan2.port_a) annotation (Line(points={{0,-10},{16,-10},{16,
          10},{30,10}}, color={0,127,255}));
  connect(tan2.port_b, port_b) annotation (Line(points={{30,-10},{60,-10},{60,0},
          {100,0}}, color={0,127,255}));
  connect(tan.heaPorVol, T_S1.port)
    annotation (Line(points={{-30,0},{-30,90},{40,90}}, color={191,0,0}));
  connect(tan1.heaPorVol, T_S2.port)
    annotation (Line(points={{0,0},{0,60},{40,60}}, color={191,0,0}));
  connect(tan2.heaPorVol, T_S3.port)
    annotation (Line(points={{30,0},{30,30},{40,30}}, color={191,0,0}));

  annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
        Rectangle(
          extent={{60,78},{50,-56}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-38,78},{60,70}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-30,78},{-40,-56}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-38,-50},{60,-58}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={255,255,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-30,-10},{50,-50}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-30,70},{50,30}},
          lineColor={255,0,0},
          fillColor={255,0,0},
          fillPattern=FillPattern.Solid),
        Rectangle(
          extent={{-30,30},{50,-10}},
          lineColor={0,0,255},
          pattern=LinePattern.None,
          fillColor={0,0,127},
          fillPattern=FillPattern.Solid)}),                      Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end storage_series;
