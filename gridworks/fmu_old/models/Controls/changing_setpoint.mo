within models.Controls;
model changing_setpoint
  Modelica.Blocks.Interfaces.RealInput u
    annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));

  Modelica.Blocks.Interfaces.BooleanOutput y
    annotation (Placement(transformation(extent={{100,-10},{120,10}})));
  Real u1, u2;
algorithm
  when sample(0,0.1) then
    u2:= u1;
    u1:= u;
  end when;

equation
  y = if (u1 > u2) then true else false;

  annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                                Rectangle(
        extent={{-100,-100},{100,100}},
        lineColor={0,0,127},
        fillColor={255,255,255},
        fillPattern=FillPattern.Solid)}),                        Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    experiment(
      StopTime=28900,
      Interval=1,
      __Dymola_Algorithm="Dassl"),
    Documentation(info="<html>
<p>The output signal becomes and remains true when there is an evolution of the real input. The deivative is not used in case the input signal is not continuous</p>
</html>"));
end changing_setpoint;
