function scenario = ValidateScenario(scenario)
%VALIDATESCENARIO Validate and normalize scenario structure.
    validateattributes(scenario, {'struct'}, {'nonempty'}, mfilename, 'scenario');

    requiredTop = ["target", "surveillanceSensor", "interceptor", "engagement", "simulation"];
    for i = 1:numel(requiredTop)
        fieldName = requiredTop(i);
        if ~isfield(scenario, fieldName)
            error("sim:ValidateScenario:MissingField", "Scenario missing required section: %s", fieldName);
        end
    end

    % Target
    scenario.target.position = localValidateVec2(scenario.target, "position", "target.position");
    scenario.target.speed = localValidateScalar(scenario.target, "speed", "target.speed", 0.0, inf, false);
    scenario.target.rcs = localValidateScalar(scenario.target, "rcs", "target.rcs", 0.0, inf, true);

    if isfield(scenario.target, "waypoints")
        wps = scenario.target.waypoints;
        if isempty(wps)
            scenario.target.waypoints = zeros(0, 2);
        else
            validateattributes(wps, {'numeric'}, {'2d', 'ncols', 2, 'finite'}, mfilename, 'target.waypoints');
            scenario.target.waypoints = wps;
        end
    else
        scenario.target.waypoints = zeros(0, 2);
    end

    % Surveillance sensor
    ss = scenario.surveillanceSensor;
    ss.position = localValidateVec2(ss, "position", "surveillanceSensor.position");
    ss.max_range = localValidateScalar(ss, "max_range", "surveillanceSensor.max_range", 0.0, inf, false);
    ss.field_of_regard_deg = localValidateScalar(ss, "field_of_regard_deg", "surveillanceSensor.field_of_regard_deg", 0.0, 360.0, true);
    ss.pd_at_max_range = localValidateScalar(ss, "pd_at_max_range", "surveillanceSensor.pd_at_max_range", 0.0, 1.0, true);
    ss.classification_accuracy = localValidateScalar(ss, "classification_accuracy", "surveillanceSensor.classification_accuracy", 0.0, 1.0, true);

    if ~isfield(ss, "noise") || isempty(ss.noise)
        ss.noise = struct();
    end
    ss.noise.range_noise_fraction = localValidateScalarWithDefault(ss.noise, "range_noise_fraction", 0.0, 0.0, inf);
    ss.noise.bearing_noise_deg = localValidateScalarWithDefault(ss.noise, "bearing_noise_deg", 0.0, 0.0, 180.0);
    ss.noise.speed_noise_fraction = localValidateScalarWithDefault(ss.noise, "speed_noise_fraction", 0.0, 0.0, inf);
    ss.noise.heading_noise_deg = localValidateScalarWithDefault(ss.noise, "heading_noise_deg", 0.0, 0.0, 180.0);
    scenario.surveillanceSensor = ss;

    % Interceptor
    ic = scenario.interceptor;
    ic.position = localValidateVec2(ic, "position", "interceptor.position");
    ic.max_speed = localValidateScalar(ic, "max_speed", "interceptor.max_speed", 0.0, inf, false);
    ic.max_turn_rate_deg = localValidateScalar(ic, "max_turn_rate_deg", "interceptor.max_turn_rate_deg", 0.0, inf, false);
    ic.kill_radius = localValidateScalar(ic, "kill_radius", "interceptor.kill_radius", 0.0, inf, false);
    ic.max_flight_time = localValidateScalar(ic, "max_flight_time", "interceptor.max_flight_time", 0.0, inf, false);

    if ~isfield(ic, "seeker") || isempty(ic.seeker)
        ic.seeker = struct();
    end
    ic.seeker.max_range = localValidateScalarWithDefault(ic.seeker, "max_range", 500.0, 0.0, inf);
    ic.seeker.field_of_regard_deg = localValidateScalarWithDefault(ic.seeker, "field_of_regard_deg", 60.0, 0.0, 360.0);
    ic.seeker.pd_at_max_range = localValidateScalarWithDefault(ic.seeker, "pd_at_max_range", 0.5, 0.0, 1.0);
    scenario.interceptor = ic;

    % Engagement
    eg = scenario.engagement;
    if ~isfield(eg, "terminal_guidance")
        error("sim:ValidateScenario:MissingField", "Scenario missing required field: engagement.terminal_guidance");
    end
    eg.terminal_guidance = lower(string(eg.terminal_guidance));
    if ~any(eg.terminal_guidance == ["proportional_nav", "pure_pursuit"])
        error("sim:ValidateScenario:InvalidValue", "engagement.terminal_guidance must be proportional_nav or pure_pursuit.");
    end
    eg.nav_gain = localValidateScalar(eg, "nav_gain", "engagement.nav_gain", 0.0, inf, false);
    eg.terminal_handover_range = localValidateScalar(eg, "terminal_handover_range", "engagement.terminal_handover_range", 0.0, inf, true);
    eg.stern_offset = localValidateScalar(eg, "stern_offset", "engagement.stern_offset", 0.0, inf, true);
    eg.approach_blend_range = localValidateScalar(eg, "approach_blend_range", "engagement.approach_blend_range", 0.0, inf, false);
    scenario.engagement = eg;

    % Simulation
    sm = scenario.simulation;
    sm.dt = localValidateScalar(sm, "dt", "simulation.dt", 0.0, inf, false);
    sm.max_time = localValidateScalar(sm, "max_time", "simulation.max_time", 0.0, inf, false);

    if ~isfield(sm, "seed")
        sm.seed = [];
    elseif ~isempty(sm.seed)
        validateattributes(sm.seed, {'numeric'}, {'scalar', 'finite', 'integer', 'nonnegative'}, mfilename, 'simulation.seed');
    end

    scenario.simulation = sm;
end

function value = localValidateScalar(s, fieldName, qualifiedName, minValue, maxValue, inclusiveLower)
    if ~isfield(s, fieldName)
        error("sim:ValidateScenario:MissingField", "Scenario missing required field: %s", qualifiedName);
    end
    value = s.(fieldName);
    validateattributes(value, {'numeric'}, {'scalar', 'real', 'finite'}, mfilename, qualifiedName);

    if inclusiveLower
        lowerOk = value >= minValue;
    else
        lowerOk = value > minValue;
    end
    if ~(lowerOk && value <= maxValue)
        error("sim:ValidateScenario:InvalidValue", "%s out of valid range.", qualifiedName);
    end
end

function value = localValidateScalarWithDefault(s, fieldName, defaultValue, minValue, maxValue)
    if ~isfield(s, fieldName)
        value = defaultValue;
        return;
    end
    value = s.(fieldName);
    validateattributes(value, {'numeric'}, {'scalar', 'real', 'finite'}, mfilename, fieldName);
    if value < minValue || value > maxValue
        error("sim:ValidateScenario:InvalidValue", "%s out of valid range.", fieldName);
    end
end

function vec = localValidateVec2(s, fieldName, qualifiedName)
    if ~isfield(s, fieldName)
        error("sim:ValidateScenario:MissingField", "Scenario missing required field: %s", qualifiedName);
    end
    vec = s.(fieldName);
    validateattributes(vec, {'numeric'}, {'vector', 'numel', 2, 'real', 'finite'}, mfilename, qualifiedName);
    vec = reshape(vec, 1, 2);
end
