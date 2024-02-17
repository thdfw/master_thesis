within models.Controls.Tests;
model try_EqualInteger
  models.Controls.EqualInteger intLesEquThr(t=5)
    annotation (Placement(transformation(extent={{-20,0},{0,20}})));
    Modelica.Blocks.Math.RealToInteger realToInteger
      annotation (Placement(transformation(extent={{-60,0},{-40,20}})));
    Modelica.Blocks.Sources.Ramp ramp(height=10, duration=1,
      offset=-10)
      annotation (Placement(transformation(extent={{-100,0},{-80,20}})));
equation
    connect(ramp.y, realToInteger.u)
      annotation (Line(points={{-79,10},{-62,10}}, color={0,0,127}));
    connect(realToInteger.y, intLesEquThr.u)
      annotation (Line(points={{-39,10},{-22,10}}, color={255,127,0}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)));
end try_EqualInteger;
