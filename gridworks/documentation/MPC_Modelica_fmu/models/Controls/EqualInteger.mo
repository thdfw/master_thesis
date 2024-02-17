within models.Controls;
block EqualInteger
  "Output y is true, if input u is less or equal than a threshold"
  parameter Integer t=0
    "Threshold for comparison";
  Buildings.Controls.OBC.CDL.Interfaces.IntegerInput u
    "Connector of Integer input signal"
    annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
  Buildings.Controls.OBC.CDL.Interfaces.BooleanOutput y
    "Connector of Boolean output signal"
    annotation (Placement(transformation(extent={{100,-20},{140,20}})));

equation
  y=u == t;
  annotation (
    defaultComponentName="intLesEquThr",
    Icon(
      coordinateSystem(
        preserveAspectRatio=true,
        extent={{-100,-100},{100,100}}),
      graphics={
        Rectangle(
          extent={{-100,100},{100,-100}},
          lineColor={0,0,0},
          lineThickness=5.0,
          fillColor={210,210,210},
          fillPattern=FillPattern.Solid,
          borderPattern=BorderPattern.Raised),
        Ellipse(
          extent={{71,7},{85,-7}},
          lineColor=DynamicSelect({235,235,235},
            if y then
              {0,255,0}
            else
              {235,235,235}),
          fillColor=DynamicSelect({235,235,235},
            if y then
              {0,255,0}
            else
              {235,235,235}),
          fillPattern=FillPattern.Solid),
        Text(
          extent={{-150,-140},{150,-110}},
          textColor={0,0,0},
          textString="%t"),
        Text(
          extent={{-150,150},{150,110}},
          textColor={0,0,255},
          textString="%name"),
        Text(
          extent={{-82,-48},{14,42}},
          textColor={255,127,0},
          textString="=")}),
    Documentation(
      info="<html>
<p>Block that outputs <span style=\"font-family: Courier New;\">true</span> if the Integer input is equal to the parameter <span style=\"font-family: Courier New;\">t</span>. Otherwise the output is <span style=\"font-family: Courier New;\">false</span>. </p>
</html>",
      revisions="<html>
<ul>
<li>
August 6, 2020, by Michael Wetter:<br/>
Renamed <code>threshold</code> to <code>t</code>.<br/>
This is for <a href=\"https://github.com/lbl-srg/modelica-buildings/issues/2076\">issue 2076</a>.
</li>
<li>
August 30, 2017, by Jianjun Hu:<br/>
First implementation, based on the implementation of the
Modelica Standard Library.
</li>
</ul>
</html>"));
end EqualInteger;
