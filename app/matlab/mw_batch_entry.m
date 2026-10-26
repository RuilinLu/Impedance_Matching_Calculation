function mw_batch_entry(input_json, output_json)
%MW_BATCH_ENTRY Run a batch of design cases and write a JSON array.
%   Used by the MCP shell to call MATLAB R2025b without a GUI.

raw = jsondecode(fileread(input_json));
cases = raw.cases;
if isstruct(cases)
    cases = num2cell(cases);
elseif ~iscell(cases)
    error('cases must be a JSON array');
end

results = cell(1, numel(cases));
for k = 1:numel(cases)
    c = cases{k};
    if isfield(c, 'L_uh') && ~isempty(c.L_uh) && ~isnan(c.L_uh)
        L = c.L_uh;
    else
        L = NaN;
    end
    if isfield(c, 'c3_pf') && ~isempty(c.c3_pf) && ~isnan(c.c3_pf)
        C3 = c.c3_pf;
    else
        C3 = NaN;
    end
    if isfield(c, 'z0') && ~isempty(c.z0)
        z0 = c.z0;
    else
        z0 = 50;
    end
    results{k} = mw_design(c.topology, c.frequency_mhz, c.load_r, ...
                           c.load_x, L, C3, z0);
end

fid = fopen(output_json, 'w', 'n', 'UTF-8');
if fid < 0
    error('Cannot open output file');
end
fprintf(fid, '%s', jsonencode(results));
fclose(fid);
end
