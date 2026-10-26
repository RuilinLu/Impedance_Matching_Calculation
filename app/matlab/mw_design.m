function out = mw_design(top, f_mhz, rl, xl, L_uh, c3_pf, z0)
%MW_DESIGN Analytical matching-network design (R2025b reference implementation).
%   The formulas mirror the V3.0 App Designer code; the result is verified with
%   an independent nodal analysis of the complete network.
%
%   Units: f_mhz in MHz, impedances in ohm, L_uh in uH, c3_pf in pF.

if nargin < 7 || isempty(z0), z0 = 50; end
out = struct('ok', false, 'message', '', 'topology', char(top));
try
    top = lower(char(top));
    if f_mhz <= 0, error('Frequency must be positive'); end
    if rl <= 0, error('Load resistance must be positive'); end
    f = f_mhz * 1e6;
    w = 2 * pi * f;
    if isempty(L_uh) || isnan(L_uh)
        error('L_uh is required');
    end
    L = L_uh * 1e-6;
    if isempty(c3_pf) || isnan(c3_pf), C3 = 0; else, C3 = c3_pf * 1e-12; end

    switch top
        case 'l_right'
            if rl >= z0, error('L-right requires R_L < Z0'); end
            Q = sqrt(z0 / rl - 1);
            C1 = Q / (z0 * w);
            d = w * L + xl - Q * rl;
            if d <= 0, error('No positive C2: L is too small'); end
            C2 = 1 / (w * d);
            C3 = 0;
        case 'l_left'
            if rl <= z0, error('L-left requires R_L > Z0'); end
            YL = 1 / (rl + 1j * xl);
            G = real(YL); B = imag(YL);
            inside = G / z0 - G * G;
            if inside < 0, error('Load conductance too large'); end
            term = sqrt(inside);
            cands = [(term - B) / w, (-term - B) / w];
            cands = cands(cands > 0);
            if isempty(cands), error('No positive C1'); end
            C1 = min(cands);
            Bch = B + w * C1;
            Zpar = 1 / (G + 1j * Bch);
            d = w * L + imag(Zpar);
            if d <= 0, error('No positive C2: L is too small'); end
            C2 = 1 / (w * d);
            C3 = 0;
            Q = abs(Bch) / G;
        case 't'
            if C3 <= 0, error('T network requires C3 > 0'); end
            Zleft = z0 - 1j / (w * C3);
            Yleft = 1 / Zleft;
            G = real(Yleft); Bleft = imag(Yleft);
            Rv = 1 / G;
            if Rv < rl, error('Virtual resistance is smaller than R_L'); end
            temp = rl / G - rl * rl;
            if temp < 0, error('Virtual resistance condition failed'); end
            mag = sqrt(temp);
            cands = [];
            if w * (xl - mag) > 0, cands(end + 1, :) = [1 / (w * (xl - mag)), mag]; end
            if w * (xl + mag) > 0, cands(end + 1, :) = [1 / (w * (xl + mag)), -mag]; end
            if isempty(cands), error('No positive C1'); end
            [~, idx] = min(cands(:, 1));
            C1 = cands(idx, 1);
            xb = cands(idx, 2);
            Bneed = -(Bleft + imag(1 / (rl + 1j * xb)));
            if abs(Bneed) < 1e-12, error('C2 is undefined'); end
            d = w * L + 1 / Bneed;
            if d <= 0, error('No positive C2: L is too large'); end
            C2 = 1 / (w * d);
            Q = abs(Bneed) * z0;
        case 'pi1'
            if C3 <= 0, error('Pi-I requires C3 > 0'); end
            YL = 1 / (rl + 1j * xl);
            G = real(YL); B = imag(YL);
            Zs = 1 / (1 / z0 + 1j * w * C3);
            delta = G / real(Zs) - G * G;
            if delta < 0, error('C3 makes the source resistance too low'); end
            term = sqrt(delta);
            cands = [(term - B) / w, (-term - B) / w];
            cands = cands(cands > 0);
            if isempty(cands), error('No positive C1'); end
            C1 = min(cands);
            Znew = 1 / (G + 1j * (B + w * C1));
            d = w * L + imag(Zs) + imag(Znew);
            if d <= 0, error('No positive C2: L is too small'); end
            C2 = 1 / (w * d);
            Q = abs(imag(Zs)) / real(Zs);
        case 'pi2'
            if C3 <= 0, error('Pi-II requires C3 > 0'); end
            ZLeff = 1 / (1 / (rl + 1j * xl) + 1j * w * C3);
            Reff = real(ZLeff); Xeff = imag(ZLeff);
            if Reff > z0, error('C3 leaves R_eff > Z0'); end
            Q = sqrt(max(z0 / Reff - 1, 0));
            C1 = Q / (z0 * w);
            Xs = -Reff * Q;
            d = w * L + Xeff + Xs;
            if d <= 0, error('No positive C2: L is too small'); end
            C2 = 1 / (w * d);
        otherwise
            error('Unknown topology');
    end

    comps = struct('L_uH', L * 1e6, 'C1_pF', C1 * 1e12, ...
                   'C2_pF', C2 * 1e12, 'C3_pF', C3 * 1e12);
    [zin, vswr, s11] = mw_analyze(top, f_mhz, rl, xl, comps, z0);

    out.ok = true;
    out.topology = top;
    out.L_uH = comps.L_uH;
    out.C1_pF = comps.C1_pF;
    out.C2_pF = comps.C2_pF;
    out.C3_pF = comps.C3_pF;
    out.zin_re = real(zin);
    out.zin_im = imag(zin);
    out.input_impedance_display = sprintf('%.6f %+.6fj', real(zin), imag(zin));
    out.vswr = vswr;
    out.s11_db = s11;
    out.q = Q;
    out.message = 'OK';
catch ME
    out.ok = false;
    out.message = ME.message;
    out.L_uH = NaN; out.C1_pF = NaN; out.C2_pF = NaN; out.C3_pF = NaN;
    out.zin_re = NaN; out.zin_im = NaN; out.vswr = NaN; out.s11_db = NaN;
    out.input_impedance_display = '';
end
end


function [zin, vswr, s11_db] = mw_analyze(top, f_mhz, rl, xl, comps, z0)
%MW_ANALYZE Nodal analysis of the lossless matching network.
w = 2 * pi * f_mhz * 1e6;
L = comps.L_uH * 1e-6;
C1 = comps.C1_pF * 1e-12;
C2 = comps.C2_pF * 1e-12;
C3 = comps.C3_pF * 1e-12;
ZL = rl + 1j * xl;
Zs = 1j * (w * L - 1 / (w * C2));

switch top
    case 'l_right'
        nodes = {'s', 'l'};
        elems = { ...
            struct('kind', 'shunt', 'a', 's', 'b', '', 'y', 1j * w * C1), ...
            struct('kind', 'series', 'a', 's', 'b', 'l', 'z', Zs)};
    case 'l_left'
        nodes = {'s', 'l'};
        elems = { ...
            struct('kind', 'series', 'a', 's', 'b', 'l', 'z', Zs), ...
            struct('kind', 'shunt', 'a', 'l', 'b', '', 'y', 1j * w * C1)};
    case 't'
        nodes = {'s', 'm', 'l'};
        elems = { ...
            struct('kind', 'series', 'a', 's', 'b', 'm', 'z', -1j / (w * C3)), ...
            struct('kind', 'series', 'a', 'm', 'b', 'l', 'z', -1j / (w * C1)), ...
            struct('kind', 'shunt', 'a', 'm', 'b', '', 'y', 1 / Zs)};
    case 'pi1'
        nodes = {'s', 'l'};
        elems = { ...
            struct('kind', 'shunt', 'a', 's', 'b', '', 'y', 1j * w * C3), ...
            struct('kind', 'series', 'a', 's', 'b', 'l', 'z', Zs), ...
            struct('kind', 'shunt', 'a', 'l', 'b', '', 'y', 1j * w * C1)};
    case 'pi2'
        nodes = {'s', 'l'};
        elems = { ...
            struct('kind', 'shunt', 'a', 's', 'b', '', 'y', 1j * w * C1), ...
            struct('kind', 'series', 'a', 's', 'b', 'l', 'z', Zs), ...
            struct('kind', 'shunt', 'a', 'l', 'b', '', 'y', 1j * w * C3)};
    otherwise
        error('Unknown topology');
end

n = numel(nodes);
Y = zeros(n, n);
Vs = 2; Rs = z0;
Y(1, 1) = Y(1, 1) + 1 / Rs;
rhs = zeros(n, 1);
rhs(1) = Vs / Rs;
for k = 1:numel(elems)
    e = elems{k};
    ia = find(strcmp(nodes, e.a));
    if strcmp(e.kind, 'series')
        ib = find(strcmp(nodes, e.b));
        y = 1 / e.z;
        Y(ia, ia) = Y(ia, ia) + y;
        Y(ib, ib) = Y(ib, ib) + y;
        Y(ia, ib) = Y(ia, ib) - y;
        Y(ib, ia) = Y(ib, ia) - y;
    else
        Y(ia, ia) = Y(ia, ia) + e.y;
    end
end
il = find(strcmp(nodes, 'l'));
Y(il, il) = Y(il, il) + 1 / ZL;
V = Y \ rhs;
Iin = (Vs - V(1)) / Rs;
zin = V(1) / Iin;
gamma = (zin - z0) / (zin + z0);
vswr = (1 + abs(gamma)) / (1 - abs(gamma));
s11_db = 20 * log10(abs(gamma) + 1e-300);
end
