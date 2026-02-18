import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

/**
 * Extension to sync OneButtonPreset widgets based on selected preset.
 */
app.registerExtension({
    name: "OneButtonPrompt.PresetSync",
    async nodeCreated(node) {
        if (node.comfyClass === "OneButtonPreset") {
            const nodeName = "OneButtonPreset";
            console.log(`[OBP Sync] Node created: ${node.id} (${node.comfyClass})`);

            // Map of internal preset keys to slider widget names
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

            const tiers = ["never", "novel", "extraordinary", "unique", "legendary", "rare", "uncommon", "normal", "common", "always"];

            /**
             * Updates all widgets on the node based on preset data.
             */
            const updateSliders = async (presetName) => {
                console.log(`[OBP Sync] Syncing preset: "${presetName}"`);

                if (presetName === "All (random)..." || presetName === "Custom...") {
                    // Reset sliders to -1 (Inherit)
                    for (const widgetName of Object.values(sliderMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        if (widget) widget.value = -1;
                    }
                    // Reset quality and density
                    const special = ["descriptor_density", "quality_chance"];
                    for (const s of special) {
                        const widget = node.widgets.find(w => w.name === s);
                        if (widget) widget.value = -1;
                    }
                    console.log("[OBP Sync] Reset sliders to -1 for random/custom preset.");
                    return;
                }

                try {
                    const response = await api.fetchApi(`/one_button_prompt/get_preset?name=${encodeURIComponent(presetName)}`);
                    if (response.status !== 200) {
                        console.error(`[OBP Sync] API error: ${response.status} ${response.statusText}`);
                        return;
                    }

                    const data = await response.json();
                    if (!data || Object.keys(data).length === 0) {
                        console.warn(`[OBP Sync] No data returned for preset: ${presetName}`);
                        return;
                    }

                    // Update Sliders
                    for (const [key, widgetName] of Object.entries(sliderMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        if (widget) {
                            if (data[key]) {
                                const val = tiers.indexOf(data[key]);
                                widget.value = val !== -1 ? val : -1;
                            } else {
                                widget.value = -1;
                            }
                        }
                    }

                    // Update Standard Fields
                    for (const [key, widgetName] of Object.entries(fieldMap)) {
                        const widget = node.widgets.find(w => w.name === widgetName);
                        if (widget && data[key] !== undefined) {
                            // Guard: for COMBO widgets, only set value if it's a valid choice
                            if (widget.options?.values) {
                                if (widget.options.values.includes(data[key])) {
                                    widget.value = data[key];
                                } else {
                                    console.warn(`[OBP Sync] Preset value "${data[key]}" not found in widget "${widgetName}" options. Skipping to avoid ghost value.`);
                                }
                            } else {
                                widget.value = data[key];
                            }
                        }
                    }

                    // Special Overrides (e.g. descriptor density which maps to subjectdescriptor1chance)
                    const densityWidget = node.widgets.find(w => w.name === "descriptor_density");
                    if (densityWidget) {
                        const dVal = data["subjectdescriptor1chance"];
                        densityWidget.value = dVal ? tiers.indexOf(dVal) : -1;
                    }
                    const qualityWidget = node.widgets.find(w => w.name === "quality_chance");
                    if (qualityWidget) {
                        const qVal = data["quality1chance"];
                        qualityWidget.value = qVal ? tiers.indexOf(qVal) : -1;
                    }

                    console.log(`[OBP Sync] Successfully synced "${presetName}"`);
                    node.setDirtyCanvas(true, true);

                } catch (error) {
                    console.error("[OBP Sync] Sync Error:", error);
                }
            };

            // Locate the preset selection widget
            let presetWidget = node.widgets.find(w => w.name === "OneButtonPreset");
            if (!presetWidget) {
                // Fallback search
                presetWidget = node.widgets.find(w => w.type === "COMBO" && w.options?.values?.includes("Standard"));
            }

            if (presetWidget) {
                console.log(`[OBP Sync] Hooking into widget: ${presetWidget.name}`);
                const originalCallback = presetWidget.callback;
                presetWidget.callback = function (value) {
                    updateSliders(value);
                    if (originalCallback) {
                        return originalCallback.apply(this, arguments);
                    }
                };

                // Debounced initial sync: wait for all widgets to be fully initialized
                // before syncing the current preset value on workflow load.
                setTimeout(() => {
                    if (presetWidget.value) {
                        updateSliders(presetWidget.value);
                    }
                }, 250);
            } else {
                console.warn("[OBP Sync] Could not find preset selection widget on OneButtonPreset node.");
            }
        }
    }
});

