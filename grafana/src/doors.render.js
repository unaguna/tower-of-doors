context = options.context;
console.debug("Start Render", context);

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

const doors = [
  'F5F4-001',
  'F5F3-001',
  'F4F3-001',
  'F4F2-001',
  'F3F2-001',
  'F3F1-001',
  'F2F1-001',
  'F5-O-000',
  'F5-O-060',
  'F5-O-120',
  'F5-O-180',
  'F5-O-240',
  'F5-O-300',
  'F5-I-000',
  'F5-I-060',
  'F5-I-120',
  'F5-I-180',
  'F5-I-240',
  'F5-I-300',
  'F4-O-000',
  'F4-O-060',
  'F4-O-120',
  'F4-O-180',
  'F4-O-240',
  'F4-O-300',
  'F3-O-000',
  'F3-O-060',
  'F3-O-120',
  'F3-O-180',
  'F3-O-240',
  'F3-O-300',
  'F2-O-000',
  'F2-O-060',
  'F2-O-120',
  'F2-O-180',
  'F2-O-240',
  'F2-O-300',
  'F1-O-000',
  'F1-O-060',
  'F1-O-120',
  'F1-O-180',
  'F1-O-240',
  'F1-O-300',
  'F1-I-000',
  'F1-I-060',
  'F1-I-120',
  'F1-I-180',
  'F1-I-240',
  'F1-I-300',
];

/*********************************************************
 * Fields of selected records
 * 
 * These objects contain values
 *********************************************************/
const fieldId = data.series[0].fields.find(f => f.name === 'id');
const fieldPassed = data.series[0].fields.find(f => f.name === 'passed');

for (const doorId of doors) {
  const doorElement = context.findElementByDoor(".doorColored", doorId, svgnode);
  const gTextElement = context.findElementByDoor(".gTextPassed", doorId, svgnode);
  const recordIndex = fieldId.values.buffer.findIndex(v => v === doorId);
  const passed = fieldPassed.values.buffer[recordIndex];
  const passedDisplayValue = fieldPassed.display(passed);
  
  context.renderDoor(doorElement, passedDisplayValue);
  context.renderDoorText(gTextElement, passedDisplayValue);
}
