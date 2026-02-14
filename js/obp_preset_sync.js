import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "OneButtonPrompt.PresetSync",
    async nodeCreated(node) {
        if (node.comfyClass === "OneButtonPreset") {
            // Attempt to find widget by name, fallback to first COMBO widget if not found
            let presetWidget = node.widgets.find(w => w.name === "OneButtonPreset");
            if (!presetWidget) {
                presetWidget = node.widgets.find(w => w.type === "COMBO");
            }

            if (!presetWidget) {
                console.warn("OBP Sync: Could not find preset widget.");
                return;
            }

            // Map of internal preset keys to slider widget names
            // Keys must match the keys in the preset JSON
            const sliderMap = {
                "outfitchance": "outfit_chance",
                "hairchance": "hair_chance",
                "accessorychance": "accessory_chance",
                "buildfacechance": "face_detail_chance",
                "humanexpressionchance": "expression_chance",
                "posechance": "pose_chance",
                "humanoidbackgroundchance": "background_chance",
                "moodchance": "mood_chance",
                "lightingchance": "lighting_chance",
                "colorschemechance": "color_scheme_chance",
                "lenschance": "lens_chance",
                "shotsizechance": "shot_size_chance",
                "artmovementchance": "art_movement_chance",
                "subjectbodytypechance": "body_type_chance",
            };

            // Map of standard preset keys to direct widget names
            const fieldMap = {
                "insanitylevel": "insanitylevel",
                "subject": "subject",
                "artist": "artist",
                "imagetype": "imagetype",
                "imagemodechance": "imagemodechance",
                "chosengender": "humanoids_gender",
                "givensubject": "custom_subject",
                "givenoutfit": "custom_outfit",
                "prefixprompt": "prompt_prefix",
                "suffixprompt": "prompt_suffix",
                "base_model": "base_model",
                "prompt_enhancer": "prompt_enhancer",
            };

            // Reverse tier mapping (name -> int)
            const tiers = ["never", "novel", "extraordinary", "unique", "legendary", "rare", "uncommon", "normal", "common", "always"];

            // Function to update sliders
            const updateSliders = async (presetName) => {
                if (presetName === "All (random)...") {
                    // Reset sliders to -1
                    for (const widgetName of Object.values(sliderMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        if (widget) widget.value = -1;
                    }
                    // Reset fields to defaults
                    const defaults = {
                        "insanitylevel": 5,
                        "subject": "------ all",
                        "artist": "all",
                        "imagetype": "all",
                        "imagemodechance": 20,
                        "chosengender": "all",
                        "givensubject": "",
                        "givenoutfit": "",
                        "prefixprompt": "",
                        "suffixprompt": "",
                        "base_model": "SDXL",
                        "prompt_enhancer": "none",
                    };
                    for (const [key, widgetName] of Object.entries(fieldMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        // map internal key 'chosengender' to 'humanoids_gender' via fieldMap
                        // The fieldMap maps 'chosengender' -> 'humanoids_gender'
                        // So if we iterate defaults with key 'chosengender', how does fieldMap help? 
                        // fieldMap is internal_key -> widget_name
                        // We need defaults to be keyed by widget name or mapped key.

                        // Let's just hardcode the resets for clarity
                        node.widgets.find(w => w.name === "insanitylevel").value = 5;
                        node.widgets.find(w => w.name === "subject").value = "------ all";
                        node.widgets.find(w => w.name === "artist").value = "all";
                        node.widgets.find(w => w.name === "imagetype").value = "all";
                        node.widgets.find(w => w.name === "imagemodechance").value = 20;
                        node.widgets.find(w => w.name === "humanoids_gender").value = "all";
                        node.widgets.find(w => w.name === "custom_subject").value = "";
                        node.widgets.find(w => w.name === "custom_outfit").value = "";
                        node.widgets.find(w => w.name === "prompt_prefix").value = "";
                        node.widgets.find(w => w.name === "prompt_suffix").value = "";
                        node.widgets.find(w => w.name === "base_model").value = "SDXL";
                        node.widgets.find(w => w.name === "prompt_enhancer").value = "none";
                        // Note: emojies etc.
                    }
                    return;
                }

                try {
                    const response = await api.fetchApi(`/one_button_prompt/get_preset?name=${encodeURIComponent(presetName)}`);
                    if (response.status !== 200) return;

                    const data = await response.json();

                    // Iterate and update sliders
                    for (const [key, widgetName] of Object.entries(sliderMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        if (widget) {
                            if (data[key]) {
                                const val = tiers.indexOf(data[key]);
                                if (val !== -1) {
                                    widget.value = val;
                                } else {
                                    widget.value = -1;
                                }
                            } else {
                                widget.value = -1;
                            }
                        }
                    }

                    // Iterate and update standard fields
                    for (const [key, widgetName] of Object.entries(fieldMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        if (widget) {
                            if (data[key] !== undefined) {
                                // COMBO widgets might need string vs index handling depending on Comfy version
                                // But usually widget.value = string works
                                widget.value = data[key];
                            }
                        }
                    }

                    // Special cases if any (e.g. descriptor density which maps to 2 keys)
                    // descriptor_density checks subjectdescriptor1chance usually.
                    const densityWidget = node.widgets.find(w => w.name === "descriptor_density");
                    if (densityWidget) {
                        if (data["subjectdescriptor1chance"]) {
                            const val = tiers.indexOf(data["subjectdescriptor1chance"]);
                            if (val !== -1) densityWidget.value = val;
                        } else {
                            densityWidget.value = -1;
                        }
                    }
                    const qualityWidget = node.widgets.find(w => w.name === "quality_chance");
                    if (qualityWidget) {
                        if (data["quality1chance"]) {
                            const val = tiers.indexOf(data["quality1chance"]);
                            if (val !== -1) qualityWidget.value = val;
                        } else {
                            qualityWidget.value = -1;
                        }
                    }


                    node.setDirtyCanvas(true, true);

                } catch (error) {
                    console.error("OBP Preset Sync Error:", error);
                }
            };

            // Initial Sync
            // We want to sync on load, but we also don't want to overwrite user's saved workflow values if they loaded a workflow.
            // However, the user request "ideally when i select a preset" implies an active action.
            // So we settle for only on change.

            // Hook into callback
            // ComfyUI widgets usually have a 'callback' property
            if (presetWidget) {
                const originalCallback = presetWidget.callback;
                presetWidget.callback = function (value) {
                    updateSliders(value);
                    if (originalCallback) {
                        return originalCallback.apply(this, arguments);
                    }
                };
            }
        }
    }
});
