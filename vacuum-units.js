/* Vacuum Units — interactive pressure unit converter.
 * Widgets are rendered server-side by hooks.py as:
 *   <span class="vacuum-units-widget" data-value-pa="..." data-unit-idx="...">
 * Click cycles through UNITS in order, updating data-unit-idx and text content.
 * Uses event delegation so Material's instant navigation needs no special handling.
 */

const UNITS = [
  { toPa: 1,           label: 'Pa' },
  { toPa: 1e-3,        label: 'mPa' },
  { toPa: 1e3,         label: 'kPa' },
  { toPa: 133.322,     label: 'Torr' },
  { toPa: 0.133322,    label: 'mTorr' },
  { toPa: 1.33322e-4,  label: 'µTorr' },
  { toPa: 101325,      label: 'atm' },
  { toPa: 1e5,         label: 'bar' },
  { toPa: 100,         label: 'mbar' },
  { toPa: 3386.389,    label: 'inHg' },
];

const SUPERSCRIPTS = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³',
  '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' };

function toSup(n) {
  return String(n).split('').map(c => SUPERSCRIPTS[c] ?? c).join('');
}

function formatValue(value) {
  if (value === 0) return '0';
  const abs = Math.abs(value);
  if (abs >= 0.001 && abs < 10000) {
    return String(parseFloat(value.toPrecision(4)));
  }
  const exp = Math.floor(Math.log10(abs));
  const coeff = value / Math.pow(10, exp);
  const cs = String(parseFloat(coeff.toPrecision(4)));
  return cs === '1' ? `10${toSup(exp)}` : `${cs} \u00d7 10${toSup(exp)}`;
}

document.addEventListener('click', (e) => {
  const span = e.target.closest('.vacuum-units-widget');
  if (!span) return;
  const valuePa = parseFloat(span.dataset.valuePa);
  let idx = (parseInt(span.dataset.unitIdx, 10) + 1) % UNITS.length;
  span.dataset.unitIdx = idx;
  const unit = UNITS[idx];
  span.textContent = `${formatValue(valuePa / unit.toPa)} ${unit.label}`;
});
