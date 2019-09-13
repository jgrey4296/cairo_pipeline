
Layer Components:
  CircleGen
  Sampling
  Displacement
  Drawing

  (Geom.Gen_grid, Geom.Gen_Lines, Geom.Gen_Rand,
  Wiggle, Displace, RotateAround, Draw,
  Colour.Cast, )

CrossCuts:
	Random.Normal

  (Random.X..., Geom.Line, Geom.Circle, Heightmap, VectorField
  Easing, 

Channels:
  IdChannel A₊
  SelectChannel B₊
  FIFOChannel C₊

  (FILOChannel, SplitChannelToX..., MergeChannel, SubDiv, Delay)

Timing:
[[ C S | Dᵢ D | D ]]

Break Condition:
      loopCount == 10

Mapping:
{ C = CircleGen,
  S = Sampling,
  Dᵢ = Displacement,
  D = Drawing }

{ C -> A₊ -> S,
  S -> B₊ -> Dᵢ,
  Dᵢ -> C₊ -> D }
