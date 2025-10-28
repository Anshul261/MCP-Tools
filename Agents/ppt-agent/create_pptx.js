// create_pptx.js
const PptxGenJS = require("pptxgenjs");

let pptx = new PptxGenJS();

// Theme: Corporate Blue
const theme = {
  colors: {
    primary: "1F4E79",
    secondary: "4472C4",
    accent: "F3A612",
    dark: "2C3E50",
    light: "ECF0F1",
    white: "FFFFFF",
    text: "333333"
  },
  typography: {
    title_size: 54,
    header_size: 40,
    body_size: 18,
    font_family: "Calibri"
  }
};

// Animation preset: Professional
const animation = {
  entrance: "slide_right",
  exit: "fade",
  emphasis: "glow",
  transition: "fade"
};

pptx.defineLayout({ name: "A4", width: 11.69, height: 8.27 });
pptx.layout = "A4";

const { colors, typography } = theme;

// Utility function to add animated text with theme styling
function addAnimatedText(slide, text, options) {
  let animOptions = {
    animate: {
      type: animation.entrance,
      duration: 0.5
    }
  };
  slide.addText(text, { ...options, ...animOptions });
}

// Slide data: titles, bullets, notes, and design hints
const slidesContent = [
  {
    title: "Artificial Intelligence in Healthcare",
    bullets: [
      "Revolutionizing patient diagnosis and treatment",
      "Enhancing healthcare delivery and management",
      "Driving innovation in medical research"
    ],
    notes:
      "Introduce the topic focusing on AI's transformative impact on healthcare. Emphasize innovation and benefits to patients and providers.",
    designHint:
      "Title slide with primary color background, white large text, balanced spacing."
  },
  {
    title: "Key Applications of AI in Healthcare",
    bullets: [
      "Medical imaging and diagnostics",
      "Personalized treatment plans",
      "Drug discovery and development",
      "Virtual health assistants"
    ],
    notes:
      "Explain various AI applications; provide concise bullet points for clarity.",
    designHint:
      "Use a white/light background with primary color headers and bullet text in text color."
  },
  {
    title: "Benefits of AI Integration",
    bullets: [
      "Improved accuracy in diagnostics",
      "Reduced human error",
      "Optimized workflow and efficiency",
      "Enhanced patient engagement"
    ],
    notes:
      "Highlight tangible benefits with a professional tone.",
    designHint:
      "Use accent color highlights for benefits to draw attention."
  },
  {
    title: "Challenges and Ethical Considerations",
    bullets: [
      "Data privacy and security concerns",
      "Bias in AI algorithms",
      "Regulatory compliance",
      "Need for human oversight"
    ],
    notes:
      "Discuss challenges openly for balanced perspective.",
    designHint:
      "Use secondary color for bullet points, keep background light."
  },
  {
    title: "Case Studies: AI Success Stories",
    bullets: [
      "AI-enabled cancer diagnostics improving detection rates",
      "Predictive analytics for patient readmission risk",
      "Robotic surgery advancements"
    ],
    notes:
      "Illustrate real-world impacts with case examples briefly.",
    designHint:
      "Include subtle accent color shapes or lines for visual interest."
  },
  {
    title: "Future Outlook",
    bullets: [
      "Growing AI adoption in telemedicine",
      "Integration with wearable health tech",
      "Expansion of AI-driven personalized medicine"
    ],
    notes:
      "Conclude with future trends to inspire confidence and interest.",
    designHint:
      "Maintain clean layout, use primary color headers."
  },
  {
    title: "Q&A",
    bullets: [
      "Thank you for your attention",
      "We welcome your questions and feedback"
    ],
    notes:
      "Encourage audience interaction and close presentation professionally.",
    designHint:
      "Use primary background with white text, minimal bullet points."
  }
];

// Create slides
slidesContent.forEach((slideData, idx) => {
  let slide = pptx.addSlide();

  // Slide transition
  slide.transition = { type: animation.transition, duration: 0.5 };

  // Title slide layout distinct style
  if (idx === 0) {
    // Title slide with primary background and white text
    slide.background = { color: colors.primary };
    addAnimatedText(slide, slideData.title, {
      x: 0.5,
      y: 1,
      w: "90%",
      h: 2,
      color: colors.white,
      fontSize: typography.title_size,
      fontFace: typography.font_family,
      bold: true,
      align: "center"
    });
    if (slideData.bullets.length) {
      let bulletText = slideData.bullets.map((b) => "• " + b).join("\n");
      addAnimatedText(slide, bulletText, {
        x: 1,
        y: 3.5,
        w: 9,
        h: 3,
        color: colors.light,
        fontSize: typography.body_size,
        fontFace: typography.font_family,
        align: "left",
        bullet: true,
        lineSpacing: 28
      });
    }
  } else if (idx === 6) {
    // Q&A slide with primary background and white text
    slide.background = { color: colors.primary };
    addAnimatedText(slide, slideData.title, {
      x: 0.5,
      y: 1,
      w: "90%",
      h: 1.5,
      color: colors.white,
      fontSize: typography.title_size,
      fontFace: typography.font_family,
      bold: true,
      align: "center"
    });
    if (slideData.bullets.length) {
      let bulletText = slideData.bullets.map((b) => "• " + b).join("\n");
      addAnimatedText(slide, bulletText, {
        x: 1.5,
        y: 3,
        w: 8,
        h: 3,
        color: colors.white,
        fontSize: typography.body_size,
        fontFace: typography.font_family,
        bullet: true,
        lineSpacing: 28,
        align: "left"
      });
    }
  } else {
    // Content slides with light background and a primary color header bar
    slide.background = { color: colors.light };

    // Header bar background shape
    slide.addShape(pptx.ShapeType.rect, {
      x: 0,
      y: 0,
      w: "100%",
      h: 1.2,
      fill: { color: colors.primary },
      line: "000000",
      lineSize: 0
    });

    // Header text white and bold
    addAnimatedText(slide, slideData.title, {
      x: 0.5,
      y: 0.2,
      w: 10.5,
      h: 1,
      color: colors.white,
      fontSize: typography.header_size,
      fontFace: typography.font_family,
      bold: true,
      align: "left",
      margin: 0
    });

    // Bullet points text color depends on slide index for emphasis
    let bulletColor = colors.text;
    if (idx === 2) bulletColor = colors.accent; // slide 3 benefits highlighted accent color
    else if (idx === 3) bulletColor = colors.secondary; // slide 4 secondary color
    else bulletColor = colors.text; // others default text color

    if (slideData.bullets.length) {
      let bulletText = slideData.bullets.map((b) => "• " + b).join("\n");
      addAnimatedText(slide, bulletText, {
        x: 0.8,
        y: 1.6,
        w: 9.5,
        h: 5,
        color: bulletColor,
        fontSize: typography.body_size,
        fontFace: typography.font_family,
        bullet: true,
        lineSpacing: 28,
        align: "left"
      });
    }

    // Accent shape for slide 5 (case studies) subtle bar or underline
    if (idx === 4) {
      slide.addShape(pptx.ShapeType.rect, {
        x: 0.5,
        y: 7.4,
        w: 10,
        h: 0.15,
        fill: { color: colors.accent },
        line: "000000",
        lineSize: 0
      });
    }
  }

  // Add speaker notes
  slide.addNotes(slideData.notes);
});

// Save the presentation to file
pptx.writeFile({ fileName: "healthcare_ai_corporate.pptx" }).then(() => {
  console.log("Presentation created successfully: healthcare_ai_corporate.pptx");
}).catch((err) => {
  console.error("Error creating presentation:", err);
});