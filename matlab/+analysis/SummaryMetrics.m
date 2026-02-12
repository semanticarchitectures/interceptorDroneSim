function metrics = SummaryMetrics(history)
%SUMMARYMETRICS Compute and print key engagement metrics.
    tgt = history.TargetPos;
    intc = history.InterceptorPos;
    ranges = hypot(tgt(:, 1) - intc(:, 1), tgt(:, 2) - intc(:, 2));

    metrics = struct();
    metrics.duration = history.TimeSeconds(end);
    metrics.finalRange = ranges(end);
    metrics.minRange = min(ranges);
    metrics.finalPhase = string(history.Phase(end));
    metrics.finalResult = string(history.Result(end));

    fprintf('----------------------------------------\n');
    fprintf('ENGAGEMENT SUMMARY\n');
    fprintf('----------------------------------------\n');
    fprintf('Duration:      %.1f s\n', metrics.duration);
    fprintf('Final range:   %.1f m\n', metrics.finalRange);
    fprintf('Minimum range: %.1f m\n', metrics.minRange);
    fprintf('Final phase:   %s\n', metrics.finalPhase);
    fprintf('Final result:  %s\n', metrics.finalResult);
    fprintf('----------------------------------------\n');
end
