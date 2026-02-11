function correct = TryClassify(sensor)
%TRYCLASSIFY Stochastic classification outcome.
    correct = rand() < sensor.classificationAccuracy;
end
