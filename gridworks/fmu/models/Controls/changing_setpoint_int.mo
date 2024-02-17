within models.Controls;
model changing_setpoint_int
  Modelica.Blocks.Interfaces.IntegerInput
                                       u
    annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));

  Modelica.Blocks.Interfaces.BooleanOutput y
    annotation (Placement(transformation(extent={{100,-10},{120,10}})));

equation
  y = change(u);
  annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
                                Rectangle(
        extent={{-100,-100},{100,100}},
        lineColor={0,0,127},
        fillColor={255,255,255},
        fillPattern=FillPattern.Solid)}),                        Diagram(
        coordinateSystem(preserveAspectRatio=false)),
    Documentation(info="<html>
<p>The output signal becomes and remains true when there is an evolution of the integer input</p>
</html>"));
end changing_setpoint_int;
