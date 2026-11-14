import { app } from "../../scripts/app.js";

const LABEL_OVERRIDES = {
    OneButtonPrompt: {
        emojis: "disable_emojis",
    },
    OneButtonPreset: {
        OneButtonPreset: "preset",
    },
    AutoNegativePrompt: {
        postive_prompt: "positive_prompt",
        enhancenegative: "enhance_negative",
        insanitylevel: "random_pruning",
    },
    OneButtonSuperPrompt: {
        superpromptstyle: "superprompt_style",
    },
};

app.registerExtension({
    name: "OneButtonPrompt.WidgetLabels",
    nodeCreated(node) {
        const overrides = LABEL_OVERRIDES[node.comfyClass];
        if (!overrides) return;
        for (const w of node.widgets ?? []) {
            if (overrides[w.name]) w.label = overrides[w.name];
        }
        for (const inp of node.inputs ?? []) {
            if (overrides[inp.name]) inp.label = overrides[inp.name];
        }
    },
});
