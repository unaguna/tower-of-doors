console.log("Start Init");
context = {};


const PASSED_CLOSED = -1;
const PASSED_NODATA = -2;
const PASSED_THRESHOLD = 300; 

const COLOR_CLOSED = svgnode.gradient('linear', function(add) {
  add.stop(0, 'rgb(18, 74, 234)');
  add.stop(1, 'rgb(63, 156, 240)');
});
const COLOR_OPEN_SHORT = svgnode.gradient('linear', function(add) {
  add.stop(0, 'rgb(66, 154, 67)');
  add.stop(1, 'rgb(111, 183, 87)');
});
const COLOR_OPEN_LONG = 'yellow';
const COLOR_NODATA = 'black';


context.findElementByDoor = (selector, doorId, svgnode) => {
  return svgnode.findOne(`${selector}[door="${doorId}"]`);
}


context.formatDisplayValue = (displayValue) =>
  `${displayValue.prefix ?? ""}${displayValue.text}${displayValue.suffix ?? ""}`;

context.renderDoor = (doorElement, passedDisplayValue) => {
  const passed = passedDisplayValue.numeric;
  if(passed == PASSED_CLOSED) {
    doorElement?.fill(COLOR_CLOSED);
  } else if (0 <= passed && passed < PASSED_THRESHOLD) {
    doorElement?.fill(COLOR_OPEN_SHORT);
  } else if (passed >= PASSED_THRESHOLD) {
    doorElement?.fill(COLOR_OPEN_LONG);
  } else {
    doorElement?.fill(COLOR_NODATA);
  }
};

context.renderDoorText = (gTextElement, passedDisplayValue) => {
  const passed = passedDisplayValue.numeric;

  const textElement = gTextElement?.findOne(".text-passed");

  textElement?.text(context.formatDisplayValue(passedDisplayValue));
  if(passed == PASSED_CLOSED) {
    gTextElement?.hide();
  } else if (0 <= passed && passed < PASSED_THRESHOLD) {
    gTextElement?.show();
  } else if (passed >= PASSED_THRESHOLD) {
    gTextElement?.show();
  } else {
    gTextElement?.hide();
  }
};


options.context = context;
console.log("End Init", context);