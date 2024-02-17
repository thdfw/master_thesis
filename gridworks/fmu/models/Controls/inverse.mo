within models.Controls;
model inverse
  Modelica.Blocks.Interfaces.RealInput u
    annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
  Modelica.Blocks.Interfaces.RealOutput y
    annotation (Placement(transformation(extent={{100,-10},{120,10}})));
equation
  y = 1-u;
  annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={Text(
          extent={{-80,40},{80,-40}},
          textColor={28,108,200},
          textString="y = 1 - u"), Rectangle(extent={{-90,40},{90,-40}},
            lineColor={28,108,200})}),                           Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end inverse;
