import subprocess

js_code = '''
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();

// Corporate Blue Theme config
const theme = {
  colors: {
    primary: "1F4E79",
    secondary: "4472C4",
    accent: "F3A612",
    dark: "2C3E50",
    light: "ECF0F1",
    white: "FFFFFF",
    text: "333333",
  },
  typography: {
    title_size: 54,
    header_size: 40,
    body_size: 18,
    font_family: "Calibri",
  },
  animations: {
    entrance: "slide_right",
    exit: "fade",
    emphasis: "glow",
    transition: "fade",
  },
};

const {colors, typography, animations} = theme;

// Global slide options
const slideOptions = {
  margin: 0.5,
  bgColor: colors.light,
  transition: { type: animations.transition, duration: 0.5 },
};

// Add slide title
function addSlideTitle(slide, titleText) {
  slide.addText(titleText, {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 1,
    fontSize: typography.header_size,
    bold: true,
    color: colors.white,
    fill: colors.primary,
    align: "center",
    fontFace: typography.font_family,
    margin: 0,
    animate: { type: animations.entrance, duration: 0.8 },
  });
}

// Add title slide title
function addTitleSlideTitle(slide, titleText) {
  slide.addText(titleText, {
    x: 0.5,
    y: 1.5,
    w: 9,
    h: 2,
    fontSize: typography.title_size,
    bold: true,
    color: colors.white,
    fontFace: typography.font_family,
    align: "center",
    animate: { type: animations.entrance, duration: 1 },
  });
}

// Add bullet points
function addBulletPoints(slide, points, x, y, w, h) {
  slide.addText(points, {
    x: x,
    y: y,
    w: w,
    h: h,
    fontSize: typography.body_size,
    color: colors.text,
    fontFace: typography.font_family,
    margin: 0.1,
    bullet: true,
    lineSpacing: 18,
    animate: { type: animations.entrance, duration: 0.7 },
  });
}

// Add speaker notes
function addSpeakerNotes(slide, notes) {
  slide.addNotes(notes);
}

// Slides data
const slidesContent = [
  { title: "Artificial Intelligence in Healthcare", subtitle: "Transforming Medical Care with Advanced Technology", speakerNotes: "Introduce the topic of AI in healthcare, overview of its transformative potential.", isTitleSlide: true },
  { title: "Introduction to AI", bulletPoints: ["Definition: Machine intelligence mimicking human cognition","Use of algorithms, machine learning, and data analytics","Key driver for digital transformation in healthcare"], speakerNotes: "Define AI and emphasize its role as a key technology transforming healthcare." },
  { title: "Applications of AI in Healthcare", bulletPoints: ["Medical Imaging & Diagnostics","Personalized Treatment & Drug Discovery","Predictive Analytics for Patient Outcomes","Virtual Health Assistants & Chatbots"], speakerNotes: "Discuss major areas where AI is applied in healthcare for improving patient care." },
  { title: "Benefits of AI Adoption", bulletPoints: ["Improved Diagnostic Accuracy","Enhanced Patient Monitoring & Care","Operational Efficiency & Cost Reduction","Accelerated Research & Innovation"], speakerNotes: "Highlight the benefits healthcare providers and patients gain from AI systems." },
  { title: "Challenges & Considerations", bulletPoints: ["Data Privacy & Security Concerns","Need for Large & Quality Data Sets","Ethical & Regulatory Frameworks","Integration with Existing Healthcare Systems"], speakerNotes: "Outline the key challenges that must be addressed for successful AI implementation." },
  { title: "Future Outlook", bulletPoints: ["Growth in AI-powered diagnostics and treatments","Increased use of AI in remote monitoring & telehealth","Collaboration between AI and healthcare professionals","Regulatory evolutions enabling innovation"], speakerNotes: "Discuss the promising future trends and directions for AI in healthcare." },
  { title: "Conclusion", bulletPoints: ["AI is revolutionizing healthcare delivery and outcomes","Balancing innovation with ethics and data security is critical","Continuous research and collaboration will drive success","Healthcare professionals must embrace AI as a tool for better patient care"], speakerNotes: "Summarize key points and emphasize the significance of AI adoption in healthcare." }
];

// Create slides

// Slide 1 - Title slide
let slide = pres.addSlide(slideOptions);
slide.background = { color: colors.primary };
addTitleSlideTitle(slide, slidesContent[0].title);
slide.addText(slidesContent[0].subtitle, {
  x: 0.5, y: 3, w: 9, h: 1,
  fontSize: 24, color: colors.light, fontFace: typography.font_family, align: "center", italic: true,
  animate: { type: animations.entrance, duration: 1 },
});
addSpeakerNotes(slide, slidesContent[0].speakerNotes);

// Remaining slides
for (let i = 1; i < slidesContent.length; i++) {
  slide = pres.addSlide(slideOptions);
  slide.addShape(pptxgen.ShapeType.rect, { x: 0, y: 0, w: 10, h: 1.2, fill: colors.primary, line: "00000033", round: 4 });
  addSlideTitle(slide, slidesContent[i].title);
  addBulletPoints(slide, slidesContent[i].bulletPoints, 0.8, 1.6, 8.4, 4);
  addSpeakerNotes(slide, slidesContent[i].speakerNotes);
}

// Save presentation
pres.writeFile({ fileName: "healthcare_ai_corporate.pptx" });
'''

# Write JavaScript code to file
with open('create_pptx.js', 'w') as f:
    f.write(js_code)

# Run the JavaScript file using Node.js
result = subprocess.run(['node', 'create_pptx.js'], capture_output=True, text=True)

# Output the stdout and stderr
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)

# Return result
result.stdout