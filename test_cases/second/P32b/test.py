from solution import read_sensor_log

out = read_sensor_log("sensor;value\ns1;0.5\ns2;0.7;extra\ns3;0.9\n")
assert out["sensor"].tolist() == ["s1", "s3"]
assert out["value"].tolist() == [0.5, 0.9]
print("PASS")
