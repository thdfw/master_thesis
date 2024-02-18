within models.Controls;
model changing_memory
  Modelica.Blocks.Interfaces.IntegerInput
                                       u
    annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));

  Modelica.Blocks.Interfaces.BooleanOutput y
    annotation (Placement(transformation(extent={{100,-100},{120,-80}})));

  Modelica.Blocks.Interfaces.BooleanOutput y__1
    annotation (Placement(transformation(extent={{100,80},{120,100}})));
  Modelica.Blocks.Interfaces.BooleanOutput y_1
    annotation (Placement(transformation(extent={{100,40},{120,60}})));
  Modelica.Blocks.Interfaces.BooleanOutput y_2
    annotation (Placement(transformation(extent={{100,0},{120,20}})));

algorithm
when change(u) then
  if u == -1 then
      y__1:=true;
  else
    y__1 :=false;
  end if;

  if u == 1 then
      y_1:=true;
  else
    y_1 :=false;
  end if;

  if u == 2 then
      y_2:=true;
  else
    y_2 :=false;
  end if;

end when;

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
<p>Whenever the value of the input varies, even just for a trigger, the value of the trigger is saved and allows to switch to another branch of the state graph in <a href=\"modelica://RTUPCM.HVAC.HPWH.Controls.rheem_proph80.cta\"> RTUPCM.HVAC.HPWS.Controls.cta</a> </p>

</html>"));
end changing_memory;
