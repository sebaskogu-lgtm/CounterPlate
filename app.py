import os
import math
from flask import Flask, render_template_string, request

app = Flask(__name__)

def calculate_creasing_specs(s, rule_pt="2PT", actual_depth=None, actual_width=None):
    rule_thickness = 0.71 if rule_pt == "2PT" else 1.05

    # 1. PERTINAX - INFINYA SPEC (Strict Table Lookup from Reference)
    inf_rule_h = 23.80
    inf_depth = s
    inf_w_par = round(rule_thickness + (1.60 * s), 2)
    inf_w_cross = round(rule_thickness + (1.85 * s), 2)
    inf_w_uni = round(math.ceil(inf_w_cross * 20) / 20, 2)

    # Infinya Table Range Mapping (from official plant table image)
    if s <= 0.35:
        inf_depth = 0.40
        inf_rule_h = 23.4
        inf_width_table = 1.30
    elif s <= 0.44:
        inf_depth = 0.40
        inf_rule_h = 23.4
        inf_width_table = 1.40
    elif s <= 0.49:
        inf_depth = 0.50
        inf_rule_h = 23.3
        inf_width_table = 1.40
    elif s <= 0.54:
        inf_depth = 0.50
        inf_rule_h = 23.3
        inf_width_table = 1.50
    elif s <= 0.60:
        inf_depth = 0.60
        inf_rule_h = 23.2
        inf_width_table = 1.60
    else:
        inf_depth = round(s, 2)
        inf_rule_h = round(23.80 - inf_depth, 1)
        inf_width_table = round(rule_thickness + (1.85 * s), 2)

    # 2. COUNTERPLATE MARBACH (Steel SRP Specification - Round Rule Heights)
    mb_depth = round(s + 0.10, 2)
    mb_rule_h = 23.6 if s <= 0.50 else 23.5
    mb_w_par = round(rule_thickness + (1.85 * s), 2)
    mb_w_cross = round(mb_w_par + 0.10, 2)
    mb_w_uni = round(math.ceil(mb_w_cross * 20) / 20, 2)

    # 3. PERTINAX - MARBACH FORMULA (Traditional Variable Rule)
    pt_depth = round(s, 2)
    pt_rule_h = round(23.80 - pt_depth, 2)
    pt_w_par = round(rule_thickness + (1.40 * s), 2)
    pt_w_cross = round(rule_thickness + (1.60 * s), 2)
    pt_w_uni = round(math.ceil(pt_w_cross * 20) / 20, 2)

    # QUALITY CONTROL AUDIT
    audit_verdict = None
    if actual_depth is not None and actual_width is not None:
        depth_dev = actual_depth - inf_depth
        width_dev = actual_width - inf_width_table
        
        if abs(depth_dev) <= 0.02 and abs(width_dev) <= 0.03:
            audit_verdict = {
                "status": "PASS",
                "style_bg": "bg-emerald-500/10",
                "style_border": "border-emerald-500/30",
                "style_text": "text-emerald-400",
                "message": "Dimensions are within optimal shop-floor manufacturing tolerances."
            }
        elif actual_depth > inf_depth and actual_width < inf_width_table:
            audit_verdict = {
                "status": "WARNING",
                "style_bg": "bg-amber-500/10",
                "style_border": "border-amber-500/30",
                "style_text": "text-amber-400",
                "message": f"Channel is over-milled in depth ({actual_depth:.2f}mm) and narrow in width ({actual_width:.2f}mm)."
            }
        else:
            audit_verdict = {
                "status": "INFO",
                "style_bg": "bg-blue-500/10",
                "style_border": "border-blue-500/30",
                "style_text": "text-blue-400",
                "message": f"Deviations detected: Depth dev = {depth_dev:+.2f}mm, Width dev = {width_dev:+.2f}mm."
            }

    return {
        "board_caliper": s,
        "rule_type": rule_pt,
        "rule_thickness": rule_thickness,
        "infinya": {
            "name": "1. Pertinax (Infinya Spec)",
            "rule_height": f"{inf_rule_h:.1f} mm",
            "rule_type": "INFINYA TABLE",
            "depth": f"{inf_depth:.2f} mm",
            "width_parallel": f"{inf_width_table:.2f} mm",
            "width_cross": f"{inf_width_table:.2f} mm",
            "width_unified": f"{inf_width_table:.2f} mm",
            "plate_thickness": "Pertinax",
            "description": f"Infinya standard table lookup for caliper {s:.2f}mm."
        },
        "marbach_cp": {
            "name": "2. Counterplate Marbach (SRP)",
            "rule_height": f"{mb_rule_h:.1f} mm",
            "rule_type": "ROUND SPEC (23.6 mm)",
            "depth": f"{mb_depth:.2f} mm",
            "width_parallel": f"{mb_w_par:.2f} mm",
            "width_cross": f"{mb_w_cross:.2f} mm",
            "width_unified": f"{mb_w_uni:.2f} mm",
            "plate_thickness": "1.00 mm Steel",
            "description": "Marbach SRP table specs adjusted to clean round shop rule heights."
        },
        "pertinax_marbach": {
            "name": "3. Pertinax (Marbach Calc)",
            "rule_height": f"{pt_rule_h:.2f} mm",
            "rule_type": "VARIABLE (23.80 - D)",
            "depth": f"{pt_depth:.2f} mm",
            "width_parallel": f"{pt_w_par:.2f} mm",
            "width_cross": f"{pt_w_cross:.2f} mm",
            "width_unified": f"{pt_w_uni:.2f} mm",
            "plate_thickness": f"{pt_depth:.2f} mm Pertinax",
            "description": "Traditional Marbach calculation where matrix thickness equals board caliper."
        },
        "audit": audit_verdict
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oman Laser - Die-Making & Counterplate Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased flex flex-col">

    <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-600/30">
                    <i class="fa-solid fa-industry text-2xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-black text-white tracking-wide">Oman Laser <span class="text-blue-500 font-normal text-sm">| Die-Making & CAD</span></h1>
                    <p class="text-xs text-slate-400">Infinya, Marbach Counterplate & Pertinax Calculator</p>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    <span class="w-2 h-2 mr-2 bg-blue-400 rounded-full animate-pulse"></span> Internal Shop Floor Engine
                </span>
            </div>
        </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        <!-- INPUT FORM -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 class="text-base font-bold text-slate-200 mb-4 flex items-center">
                <i class="fa-solid fa-sliders text-blue-400 mr-2"></i> Input Job Parameters
            </h2>
            
            <form method="POST" action="/" class="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        Board Caliper (s) [mm]
                    </label>
                    <div class="relative">
                        <input type="number" step="0.01" min="0.10" max="1.50" name="caliper" 
                               value="{{ data.board_caliper }}" required
                               class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white font-bold text-lg focus:ring-2 focus:ring-blue-500 outline-none">
                        <span class="absolute right-3 top-3 text-xs text-slate-500 font-bold">mm</span>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        Creasing Rule Thickness
                    </label>
                    <select name="rule_pt" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white font-medium focus:ring-2 focus:ring-blue-500 outline-none">
                        <option value="2PT" {% if data.rule_type == '2PT' %}selected{% endif %}>2PT (0.71 mm)</option>
                        <option value="3PT" {% if data.rule_type == '3PT' %}selected{% endif %}>3PT (1.05 mm)</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        Actual Depth [mm] <span class="text-slate-500">(QC Audit)</span>
                    </label>
                    <input type="number" step="0.01" name="actual_depth" value="{{ request.form.get('actual_depth', '') }}"
                           placeholder="e.g. 0.50"
                           class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        Actual Width [mm] <span class="text-slate-500">(QC Audit)</span>
                    </label>
                    <div class="flex space-x-2">
                        <input type="number" step="0.01" name="actual_width" value="{{ request.form.get('actual_width', '') }}"
                               placeholder="e.g. 1.47"
                               class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none">
                        <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2.5 rounded-xl transition shadow-lg shadow-blue-600/30 flex items-center">
                            <i class="fa-solid fa-calculator mr-2"></i> Calculate
                        </button>
                    </div>
                </div>
            </form>
        </div>

        {% if data.audit %}
        <div class="p-4 rounded-xl border {{ data.audit.style_bg }} {{ data.audit.style_border }} {{ data.audit.style_text }} flex items-start space-x-3">
            <i class="fa-solid fa-triangle-exclamation text-xl mt-0.5"></i>
            <div>
                <h4 class="font-bold text-sm uppercase tracking-wider">Quality Control Audit: {{ data.audit.status }}</h4>
                <p class="text-sm mt-0.5 text-slate-300">{{ data.audit.message }}</p>
            </div>
        </div>
        {% endif %}

        <!-- COMPARISON CARDS -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- 1. PERTINAX - INFINYA -->
            <div class="bg-slate-900 border-2 border-blue-500/50 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between shadow-2xl">
                <div class="absolute top-0 right-0 bg-blue-600 text-white text-[10px] font-black uppercase px-3 py-1 rounded-bl-xl tracking-wider">
                    INFINYA SPEC
                </div>
                <div>
                    <div class="flex items-center space-x-2 mb-2">
                        <i class="fa-solid fa-file-lines text-blue-400"></i>
                        <h3 class="font-bold text-lg text-white">1. Pertinax (Infinya)</h3>
                    </div>
                    <p class="text-xs text-slate-400 mb-6">{{ data.infinya.description }}</p>
                    <div class="space-y-4">
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                            <span class="text-xs text-slate-500 font-medium block">Creasing Rule Height (Die)</span>
                            <span class="text-xl font-black text-blue-400">{{ data.infinya.rule_height }}</span>
                            <span class="text-[10px] text-emerald-400 font-bold block mt-0.5">Infinya Table Spec</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">Material</span>
                                <span class="text-sm font-bold text-slate-200">Pertinax</span>
                            </div>
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">Channel Depth (D)</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.infinya.depth }}</span>
                            </div>
                        </div>
                        <div class="bg-slate-950/50 p-4 rounded-xl border border-slate-800 space-y-2">
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">Width:</span>
                                <span class="font-bold text-slate-100">{{ data.infinya.width_unified }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. COUNTERPLATE MARBACH -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between shadow-2xl">
                <div class="absolute top-0 right-0 bg-amber-600 text-white text-[10px] font-black uppercase px-3 py-1 rounded-bl-xl tracking-wider">
                    MARBACH SRP TABLE
                </div>
                <div>
                    <div class="flex items-center space-x-2 mb-2">
                        <i class="fa-solid fa-bolt text-amber-400"></i>
                        <h3 class="font-bold text-lg text-white">2. Counterplate Marbach</h3>
                    </div>
                    <p class="text-xs text-slate-400 mb-6">{{ data.marbach_cp.description }}</p>
                    <div class="space-y-4">
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                            <span class="text-xs text-slate-500 font-medium block">Creasing Rule Height (Die)</span>
                            <span class="text-xl font-black text-amber-400">{{ data.marbach_cp.rule_height }}</span>
                            <span class="text-[10px] text-amber-400 font-bold block mt-0.5">Round Shop Standard</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">Plate Base</span>
                                <span class="text-sm font-bold text-slate-200">1.00 mm Steel</span>
                            </div>
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">Channel Depth (D)</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.marbach_cp.depth }}</span>
                            </div>
                        </div>
                        <div class="bg-slate-950/50 p-4 rounded-xl border border-slate-800 space-y-2">
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">Parallel:</span>
                                <span class="font-bold text-slate-100">{{ data.marbach_cp.width_parallel }}</span>
                            </div>
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">Cross-grain:</span>
                                <span class="font-bold text-slate-100">{{ data.marbach_cp.width_cross }}</span>
                            </div>
                            <div class="pt-2 border-t border-slate-800 flex justify-between items-center text-xs">
                                <span class="text-amber-400 font-bold">Unified Width:</span>
                                <span class="font-black text-amber-300 text-sm">{{ data.marbach_cp.width_unified }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 3. PERTINAX - MARBACH FORMULA -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
                <div>
                    <div class="flex items-center space-x-2 mb-2">
                        <i class="fa-solid fa-sheet-plastic text-purple-400"></i>
                        <h3 class="font-bold text-lg text-white">3. Pertinax (Marbach Calc)</h3>
                    </div>
                    <p class="text-xs text-slate-400 mb-6">{{ data.pertinax_marbach.description }}</p>
                    <div class="space-y-4">
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                            <span class="text-xs text-slate-500 font-medium block">Creasing Rule Height (Die)</span>
                            <span class="text-xl font-black text-purple-400">{{ data.pertinax_marbach.rule_height }}</span>
                            <span class="text-[10px] text-purple-400 font-bold block mt-0.5">Variable (23.80 - D)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">Matrix Material</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.pertinax_marbach.plate_thickness }}</span>
                            </div>
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">Channel Depth (D)</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.pertinax_marbach.depth }}</span>
                            </div>
                        </div>
                        <div class="bg-slate-950/50 p-4 rounded-xl border border-slate-800 space-y-2">
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">Parallel:</span>
                                <span class="font-bold text-slate-100">{{ data.pertinax_marbach.width_parallel }}</span>
                            </div>
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">Cross-grain:</span>
                                <span class="font-bold text-slate-100">{{ data.pertinax_marbach.width_cross }}</span>
                            </div>
                            <div class="pt-2 border-t border-slate-800 flex justify-between items-center text-xs">
                                <span class="text-purple-400 font-bold">Unified Width:</span>
                                <span class="font-black text-purple-300 text-sm">{{ data.pertinax_marbach.width_unified }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SUMMARY COMPARISON TABLE -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl overflow-hidden">
            <h3 class="text-base font-bold text-white mb-4 flex items-center">
                <i class="fa-solid fa-table-list text-blue-400 mr-2"></i> Comprehensive Specification Matrix
            </h3>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-300">
                    <thead class="bg-slate-950 text-xs text-slate-400 uppercase tracking-wider border-b border-slate-800">
                        <tr>
                            <th class="px-4 py-3">Methodology Profile</th>
                            <th class="px-4 py-3">Base Material</th>
                            <th class="px-4 py-3">Rule Height in Die</th>
                            <th class="px-4 py-3">Channel Depth (D)</th>
                            <th class="px-4 py-3">Parallel Width</th>
                            <th class="px-4 py-3">Cross-Grain Width</th>
                            <th class="px-4 py-3">Unified Width</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800/60">
                        <tr class="hover:bg-slate-800/30 font-medium">
                            <td class="px-4 py-3 text-blue-400 font-bold flex items-center">
                                <span class="w-2 h-2 rounded-full bg-blue-400 mr-2"></span> 1. Pertinax (Infinya)
                            </td>
                            <td class="px-4 py-3">Pertinax</td>
                            <td class="px-4 py-3 text-emerald-400 font-bold">{{ data.infinya.rule_height }} (Table)</td>
                            <td class="px-4 py-3">{{ data.infinya.depth }}</td>
                            <td class="px-4 py-3">-</td>
                            <td class="px-4 py-3">-</td>
                            <td class="px-4 py-3 text-blue-300 font-bold">{{ data.infinya.width_unified }}</td>
                        </tr>
                        <tr class="hover:bg-slate-800/30">
                            <td class="px-4 py-3 text-amber-400 font-bold flex items-center">
                                <span class="w-2 h-2 rounded-full bg-amber-400 mr-2"></span> 2. Counterplate Marbach (SRP)
                            </td>
                            <td class="px-4 py-3">1.00 mm Steel</td>
                            <td class="px-4 py-3 text-amber-400 font-bold">{{ data.marbach_cp.rule_height }} (Round)</td>
                            <td class="px-4 py-3">{{ data.marbach_cp.depth }}</td>
                            <td class="px-4 py-3">{{ data.marbach_cp.width_parallel }}</td>
                            <td class="px-4 py-3">{{ data.marbach_cp.width_cross }}</td>
                            <td class="px-4 py-3 text-amber-300 font-bold">{{ data.marbach_cp.width_unified }}</td>
                        </tr>
                        <tr class="hover:bg-slate-800/30 text-slate-400">
                            <td class="px-4 py-3 text-purple-400 font-bold flex items-center">
                                <span class="w-2 h-2 rounded-full bg-purple-400 mr-2"></span> 3. Pertinax (Marbach Calc)
                            </td>
                            <td class="px-4 py-3">{{ data.pertinax_marbach.plate_thickness }}</td>
                            <td class="px-4 py-3 text-purple-400 font-bold">{{ data.pertinax_marbach.rule_height }} (Variable)</td>
                            <td class="px-4 py-3">{{ data.pertinax_marbach.depth }}</td>
                            <td class="px-4 py-3">{{ data.pertinax_marbach.width_parallel }}</td>
                            <td class="px-4 py-3">{{ data.pertinax_marbach.width_cross }}</td>
                            <td class="px-4 py-3 text-purple-300 font-bold">{{ data.pertinax_marbach.width_unified }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

    </main>

    <footer class="border-t border-slate-800 py-4 text-center text-xs text-slate-500">
        Oman Laser • Die-Making & CAD Engine • English Shop Edition
    </footer>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    caliper = 0.40
    rule_pt = "2PT"
    actual_depth = None
    actual_width = None

    if request.method == 'POST':
        try:
            caliper = float(request.form.get('caliper', 0.40))
            rule_pt = request.form.get('rule_pt', '2PT')
            
            ad = request.form.get('actual_depth')
            if ad and ad.strip():
                actual_depth = float(ad)
                
            aw = request.form.get('actual_width')
            if aw and aw.strip():
                actual_width = float(aw)
        except ValueError:
            pass

    data = calculate_creasing_specs(caliper, rule_pt, actual_depth, actual_width)
    return render_template_string(HTML_TEMPLATE, data=data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
