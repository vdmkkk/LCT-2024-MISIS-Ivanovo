// @ts-nocheck //
const green = { r: 0, g: 255, b: 0 };
const yellow = { r: 255, g: 255, b: 0 };
const red = { r: 255, g: 0, b: 0 };

const interpolateColor = (color1, color2, factor) => {
  const r = Math.round(color1.r + factor * (color2.r - color1.r));
  const g = Math.round(color1.g + factor * (color2.g - color1.g));
  const b = Math.round(color1.b + factor * (color2.b - color1.b));
  return { r, g, b };
};

const rgbToHex = (r, g, b) => {
  const toHex = (value) => {
    const hex = value.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
};

const getHeatmapColor = (value) => {
  if (value < 0 || value > 1) {
    throw new Error('Value must be between 0 and 1');
  }

  let color;
  if (value <= 0.5) {
    // Interpolate between green and yellow
    color = interpolateColor(green, yellow, value * 2);
  } else {
    // Interpolate between yellow and red
    color = interpolateColor(yellow, red, (value - 0.5) * 2);
  }

  return rgbToHex(color.r, color.g, color.b);
};

export default getHeatmapColor;
