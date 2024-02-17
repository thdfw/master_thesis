within models.HPWH;
package Examples
extends Modelica.Icons.ExamplesPackage;
  model HPWS_cta_several
    Modelica.Blocks.Sources.CombiTimeTable combiTimeTable(
      tableOnFile=true,
      tableName="tab1",
      fileName="C:/drive/python/HPWHS/input.txt",
      columns={2,3,4,5,6,7,8})
      annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
    Buildings.Fluid.Sources.MassFlowSource_T boundary(
      redeclare package Medium = Buildings.Media.Water,
      use_m_flow_in=true,
      use_T_in=true,
      nPorts=1)
      annotation (Placement(transformation(extent={{-80,10},{-60,30}})));
    Buildings.Fluid.Sources.Boundary_pT bou(redeclare package Medium =
          Buildings.Media.Water, nPorts=1)
      annotation (Placement(transformation(extent={{20,10},{0,30}})));
    HPWH_virtual HPHW_virtual1(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      QHeaPum_flow_nominal=1230.9,
      Qres_nominal=3800,
      VTan=0.28,
      hTan=1.3,
      dIns=0.028146574,
      cut_temperature=275.9,
      deadband_hp=13,
      deadband_low_stratification=3.5,
      res_deadband=11.25,
      res_deadband_hpactive=11.25,
      hp_timewindow=300)
      annotation (Placement(transformation(extent={{-40,8},{-20,30}})));
    Modelica.Blocks.Sources.IntegerExpression integerExpression
      annotation (Placement(transformation(extent={{20,40},{0,60}})));
  equation
    connect(combiTimeTable.y[1], boundary.m_flow_in) annotation (Line(points={{-79,90},
            {-70,90},{-70,50},{-90,50},{-90,28},{-82,28}},         color={0,0,
            127}));
    connect(combiTimeTable.y[2], boundary.T_in) annotation (Line(points={{-79,90},
            {-70,90},{-70,50},{-90,50},{-90,24},{-82,24}},   color={0,0,127}));
    connect(HPHW_virtual1.port_a, boundary.ports[1])
      annotation (Line(points={{-40,20},{-60,20}}, color={0,127,255}));
    connect(HPHW_virtual1.port_b, bou.ports[1])
      annotation (Line(points={{-20,20},{0,20}}, color={0,127,255}));
    connect(integerExpression.y, HPHW_virtual1.cta_signal) annotation (Line(
          points={{-1,50},{-30,50},{-30,32}}, color={255,127,0}));
    connect(combiTimeTable.y[3], HPHW_virtual1.Toutside) annotation (Line(
          points={{-79,90},{-50,90},{-50,30},{-42,30}}, color={0,0,127}));
    connect(combiTimeTable.y[7],HPHW_virtual1.Tevap)  annotation (Line(points={
            {-79,90},{-50,90},{-50,27},{-42,27}}, color={0,0,127}));
    connect(combiTimeTable.y[4], HPHW_virtual1.Tset_user) annotation (Line(
          points={{-79,90},{-50,90},{-50,24},{-42,24}}, color={0,0,127}));
    connect(combiTimeTable.y[5], HPHW_virtual1.Tdelta) annotation (Line(points=
            {{-79,90},{-50,90},{-50,16},{-42,16}}, color={0,0,127}));
    connect(combiTimeTable.y[6], HPHW_virtual1.Tambient) annotation (Line(
          points={{-79,90},{-50,90},{-50,11},{-42,11}}, color={0,0,127}));
    annotation (
      Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)),
      experiment(
        StopTime=50000,
        Interval=15,
        __Dymola_Algorithm="Dassl"));
  end HPWS_cta_several;

  model comp_pyt_mod
    Modelica.Blocks.Sources.CombiTimeTable combiTimeTable(
      tableOnFile=true,
      tableName="tab1",
      fileName="C:/drive/python/HPWHS/input.txt",
      columns={2,3,4,5,6,7})
      annotation (Placement(transformation(extent={{-100,80},{-80,100}})));
    Buildings.Fluid.Sources.MassFlowSource_T boundary(
      redeclare package Medium = Buildings.Media.Water,
      use_m_flow_in=true,
      use_T_in=true,
      nPorts=1)
      annotation (Placement(transformation(extent={{-80,10},{-60,30}})));
    Buildings.Fluid.Sources.Boundary_pT bou(redeclare package Medium =
          Buildings.Media.Water, nPorts=1)
      annotation (Placement(transformation(extent={{20,10},{0,30}})));
    HPWH_virtual HPHW_virtual1(
      redeclare package Medium = Buildings.Media.Water,
      m_flow_nominal=1,
      QHeaPum_flow_nominal=1230.9,
      Qres_nominal=3800,
      VTan=0.28,
      hTan=1.3,
      dIns=0.028146574,
      cut_temperature=275.9,
      deadband_hp=13,
      deadband_low_stratification=3.5,
      res_deadband=11.25,
      res_deadband_hpactive=11.25,
      hp_timewindow=300,
      nSeg=9)
      annotation (Placement(transformation(extent={{-40,8},{-20,30}})));
    Modelica.Blocks.Sources.IntegerExpression integerExpression
      annotation (Placement(transformation(extent={{20,40},{0,60}})));
    Modelica.Blocks.Sources.CombiTimeTable combipyt(
      tableOnFile=true,
      tableName="tab1",
      fileName="C:/git/hpwhs/comparison/T_pyt_1week.txt",
      columns={2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21})
      annotation (Placement(transformation(extent={{-100,-30},{-80,-10}})));
    Modelica.Blocks.Interfaces.RealOutput y_T[20](
      final quantity="ThermodynamicTemperature",
      final unit="K",
      displayUnit="degC")
      annotation (Placement(transformation(extent={{-40,-30},{-20,-10}})));
    Modelica.Blocks.Sources.CombiTimeTable combipyt1(
      tableOnFile=true,
      tableName="tab1",
      fileName="C:/git/hpwhs/comparison/HP_pyt_1week.txt",
      columns={2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21})
      annotation (Placement(transformation(extent={{-100,-60},{-80,-40}})));
    Modelica.Blocks.Interfaces.RealOutput y_HP_pyt[20]
      annotation (Placement(transformation(extent={{-40,-60},{-20,-40}})));
    Modelica.Blocks.Sources.CombiTimeTable combipyt2(
      tableOnFile=true,
      tableName="tab1",
      fileName="C:/git/hpwhs/comparison/res_pyt_1week.txt",
      columns={2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21})
      annotation (Placement(transformation(extent={{-100,-90},{-80,-70}})));
    Modelica.Blocks.Interfaces.RealOutput y_res_pyt[20]
      annotation (Placement(transformation(extent={{-40,-90},{-20,-70}})));

      Modelica.Units.SI.Temperature T_mean;
        Real T_sum;
        Real y_charge;
   Real y_charge_tot;
    Real y_charge_avg;
     Real y_charge_tot_pyt;
    Real y_charge_avg_pyt;

    Modelica.Blocks.Sources.CombiTimeTable combipyt3(
      tableOnFile=true,
      tableName="tab1",
      fileName="C:/git/hpwhs/comparison/charge_pyt_1week.txt",
      columns={2})
      annotation (Placement(transformation(extent={{20,-30},{40,-10}})));
    Modelica.Blocks.Interfaces.RealOutput y_charge_pyt
      annotation (Placement(transformation(extent={{80,-30},{100,-10}})));
  algorithm
    for k in 1:20 loop
      T_sum := T_sum + HPHW_virtual1.y[k];
    end for;
  equation
    for k in 1:20 loop
      connect(combipyt.y[k], y_T[20 + 1 - k]) annotation (Line(points={{-79,-20},{
              -54,-20},{-54,-15.25},{-30,-15.25}}, color={0,0,127}));
      y_HP_pyt[20 + 1 - k] = combipyt1.y[k] * 1000 * 3600 / 15;
      y_res_pyt[20 + 1 - k] = combipyt2.y[k] * 1000 * 3600 / 15;
    end for;
    connect(combiTimeTable.y[1], boundary.m_flow_in) annotation (Line(points={{-79,90},
            {-70,90},{-70,50},{-90,50},{-90,28},{-82,28}},         color={0,0,
            127}));
    connect(combiTimeTable.y[2], boundary.T_in) annotation (Line(points={{-79,90},
            {-70,90},{-70,50},{-90,50},{-90,24},{-82,24}},   color={0,0,127}));
    connect(HPHW_virtual1.port_a, boundary.ports[1])
      annotation (Line(points={{-40,20},{-60,20}}, color={0,127,255}));
    connect(HPHW_virtual1.port_b, bou.ports[1])
      annotation (Line(points={{-20,20},{0,20}}, color={0,127,255}));
    connect(combiTimeTable.y[3], HPHW_virtual1.Toutside) annotation (Line(
          points={{-79,90},{-50,90},{-50,30},{-42,30}}, color={0,0,127}));
    connect(combiTimeTable.y[6],HPHW_virtual1.Tevap)  annotation (Line(points
          ={{-79,90},{-50,90},{-50,27},{-42,27}}, color={0,0,127}));
    connect(combiTimeTable.y[4], HPHW_virtual1.Tset_user) annotation (Line(
          points={{-79,90},{-50,90},{-50,24},{-42,24}}, color={0,0,127}));
    connect(combiTimeTable.y[5], HPHW_virtual1.Tambient) annotation (Line(
          points={{-79,90},{-50,90},{-50,11},{-42,11}}, color={0,0,127}));
    connect(integerExpression.y, HPHW_virtual1.cta_signal) annotation (Line(
          points={{-1,50},{-30,50},{-30,32}}, color={255,127,0}));
          T_mean = T_sum / HPHW_virtual1.tank_nSeg;
          y_charge = (T_mean - combiTimeTable.y[2]) / (51.6+273.15 - combiTimeTable.y[2]) * 100;
          der(y_charge_tot) = y_charge;
          y_charge_avg = y_charge_tot / max(0.1, time);
          der(y_charge_tot_pyt) = y_charge_pyt;
          y_charge_avg_pyt = y_charge_tot_pyt / max(0.1, time);
    connect(combipyt3.y[1], y_charge_pyt)
      annotation (Line(points={{41,-20},{90,-20}}, color={0,0,127}));
    annotation (
      Icon(coordinateSystem(preserveAspectRatio=false)),
      Diagram(coordinateSystem(preserveAspectRatio=false)),
      experiment(
        StopTime=604800,
        Interval=15,
        __Dymola_Algorithm="Dassl"),
      __Dymola_experimentSetupOutput(events=false));
  end comp_pyt_mod;
end Examples;
