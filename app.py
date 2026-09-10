import os
import math
from flask import Flask, render_template_string, request

app = Flask(__name__)

def calculate_creasing_specs(s, rule_pt="2PT", actual_depth=None, actual_width=None):
    rule_thickness = 0.71 if rule_pt == "2PT" else 1.05

    # 1. SHOP FLOOR SPECIFICATION (Steel 1.00mm - Fixed 23.80mm Rule)
    sf_rule_h = 23.80
    sf_depth = round(math.ceil((s + 0.10) * 20) / 20, 2)
    sf_w_par = round(rule_thickness + (1.60 * s), 2)
    sf_w_cross = round(rule_thickness + (1.85 * s), 2)
    sf_w_uni = round(math.ceil(sf_w_cross * 20) / 20, 2)

    # 2. MARBACH SPECIFICATION (Steel 1.00mm - Reduced Rule Height)
    mb_depth = round(s + 0.05, 2)
    if s <= 0.35:
        mb_rule_h = 23.60
    elif s <= 0.50:
        mb_rule_h = 23.65
    else:
        mb_rule_h = 23.70

    mb_w_par = round(rule_thickness + (1.50 * s), 2)
    mb_w_cross = round(rule_thickness + (1.75 * s), 2)
    mb_w_uni = round(math.ceil(mb_w_cross * 20) / 20, 2)

    # 3. PERTINAX COUNTERPLATE (Variable Rule Height)
    pt_depth = round(s, 2)
    pt_rule_h = round(23.80 - pt_depth, 2)
    pt_w_par = round(rule_thickness + (1.40 * s), 2)
    pt_w_cross = round(rule_thickness + (1.60 * s), 2)
    pt_w_uni = round(math.ceil(pt_w_cross * 20) / 20, 2)

    # AUDIT VERDICT
    audit_verdict = None
    if actual_depth is not None and actual_width is not None:
        depth_dev = actual_depth - sf_depth
        width_dev = actual_width - sf_w_cross
        
        if abs(depth_dev) <= 0.02 and abs(width_dev) <= 0.03:
            audit_verdict = {
                "status": "תקין (PASS)",
                "style_bg": "bg-emerald-500/10",
                "style_border": "border-emerald-500/30",
                "style_text": "text-emerald-400",
                "message": "מידות הצילינדר והערוץ נמצאות בתוך טווח הטולרנס האופטימלי לייצור."
            }
        elif actual_depth > sf_depth and actual_width < sf_w_cross:
            audit_verdict = {
                "status": "אזהרה (WARNING)",
                "style_bg": "bg-amber-500/10",
                "style_border": "border-amber-500/30",
                "style_text": "text-amber-400",
                "message": f"עומק החרסום עמוק מדי ({actual_depth:.2f}mm) והרוחב צר ({actual_width:.2f}mm). סכנה לחוסר סימון או חניקת הקרטון בגובה סכין 23.80mm!"
            }
        elif actual_width < sf_w_par:
            audit_verdict = {
                "status": "קריטי (ALERT)",
                "style_bg": "bg-rose-500/10",
                "style_border": "border-rose-500/30",
                "style_text": "text-rose-400",
                "message": f"הרוחב ({actual_width:.2f}mm) צר מדי עבור עובי קרטון של {s:.2f}mm. סיכון גבוה לקריעת סיבי הקרטון."
            }
        else:
            audit_verdict = {
                "status": "מידע (INFO)",
                "style_bg": "bg-blue-500/10",
                "style_border": "border-blue-500/30",
                "style_text": "text-blue-400",
                "message": f"סטיות שנמדדו: סטיית עומק = {depth_dev:+.2f}mm, סטיית רוחב = {width_dev:+.2f}mm. יש לכוון את לחץ המכונה בהתאם."
            }

    return {
        "board_caliper": s,
        "rule_type": rule_pt,
        "rule_thickness": rule_thickness,
        "shop_floor": {
            "name": "Steel Counterplate (Shop Floor Spec)",
            "rule_height": f"{sf_rule_h:.2f} mm",
            "rule_type": "קבוע (23.80 mm)",
            "depth": f"{sf_depth:.2f} mm",
            "width_parallel": f"{sf_w_par:.2f} mm",
            "width_cross": f"{sf_w_cross:.2f} mm",
            "width_unified": f"{sf_w_uni:.2f} mm",
            "plate_thickness": "1.00 mm Steel",
            "description": "מומלץ לייצור רציף, יציבות מקסימלית במפעל ואפס שינויים בעץ המשטח."
        },
        "marbach": {
            "name": "Steel Counterplate (Marbach Spec)",
            "rule_height": f"{mb_rule_h:.2f} mm",
            "rule_type": "מונמך (Variable)",
            "depth": f"{mb_depth:.2f} mm",
            "width_parallel": f"{mb_w_par:.2f} mm",
            "width_cross": f"{mb_w_cross:.2f} mm",
            "width_unified": f"{mb_w_uni:.2f} mm",
            "plate_thickness": "1.00 mm Steel",
            "description": "מיועד למהירויות עבודה גבוהות. דורש סכינים מונמכות מיוחדות בשטנץ."
        },
        "pertinax": {
            "name": "Pertinax Matrix (Traditional)",
            "rule_height": f"{pt_rule_h:.2f} mm",
            "rule_type": "משתנה (23.80 - D)",
            "depth": f"{pt_depth:.2f} mm",
            "width_parallel": f"{pt_w_par:.2f} mm",
            "width_cross": f"{pt_w_cross:.2f} mm",
            "width_unified": f"{pt_w_uni:.2f} mm",
            "plate_thickness": f"{pt_depth:.2f} mm Pertinax",
            "description": "מטריצת פרטינקס מסורתית. גובה הסכין משתנה בהתאם לעובי הערוץ."
        },
        "audit": audit_verdict
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="he" dir="rtl" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>אומן לייזר - מחשבון שטנצים וצילינדרים</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap');
        body { font-family: 'Heebo', sans-serif; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased flex flex-col">

    <!-- HEADER OMAN LASER -->
    <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <div class="flex items-center space-x-4 space-x-reverse">
                <div class="p-2.5 bg-blue-600 text-white rounded-xl shadow-lg shadow-blue-600/30">
                    <i class="fa-solid fa-industry text-2xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-black text-white tracking-wide">אומן לייזר <span class="text-blue-500 font-normal text-sm">| Oman Laser</span></h1>
                    <p class="text-xs text-slate-400">מערכת חישוב פרמטרים לצילינדרים (Steel Counterplate) ופרטינקס</p>
                </div>
            </div>
            <div class="flex items-center space-x-3 space-x-reverse">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    <span class="w-2 h-2 ml-2 bg-blue-400 rounded-full animate-pulse"></span> כלי פנימי לבית המלאכה
                </span>
            </div>
        </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        <!-- INPUT FORM -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h2 class="text-base font-bold text-slate-200 mb-4 flex items-center">
                <i class="fa-solid fa-sliders text-blue-400 ml-2"></i> הזנת נתוני עבודה
            </h2>
            
            <form method="POST" action="/" class="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        עובי הקרטון (s) [מ"מ]
                    </label>
                    <div class="relative">
                        <input type="number" step="0.01" min="0.10" max="1.50" name="caliper" 
                               value="{{ data.board_caliper }}" required
                               class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white font-bold text-lg focus:ring-2 focus:ring-blue-500 outline-none">
                        <span class="absolute left-3 top-3 text-xs text-slate-500 font-bold">mm</span>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        עובי סכין ביג
                    </label>
                    <select name="rule_pt" class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white font-medium focus:ring-2 focus:ring-blue-500 outline-none">
                        <option value="2PT" {% if data.rule_type == '2PT' %}selected{% endif %}>2PT (0.71 mm)</option>
                        <option value="3PT" {% if data.rule_type == '3PT' %}selected{% endif %}>3PT (1.05 mm)</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        עומק בפועל [מ"מ] <span class="text-slate-500">(בדיקת איכות)</span>
                    </label>
                    <input type="number" step="0.01" name="actual_depth" value="{{ request.form.get('actual_depth', '') }}"
                           placeholder="דוגמה: 0.50"
                           class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none">
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 mb-2">
                        רוחב בפועל [מ"מ] <span class="text-slate-500">(בדיקת איכות)</span>
                    </label>
                    <div class="flex space-x-2 space-x-reverse">
                        <input type="number" step="0.01" name="actual_width" value="{{ request.form.get('actual_width', '') }}"
                               placeholder="דוגמה: 1.47"
                               class="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none">
                        <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 py-2.5 rounded-xl transition shadow-lg shadow-blue-600/30 flex items-center">
                            <i class="fa-solid fa-calculator ml-2"></i> חשב
                        </button>
                    </div>
                </div>
            </form>
        </div>

        {% if data.audit %}
        <div class="p-4 rounded-xl border {{ data.audit.style_bg }} {{ data.audit.style_border }} {{ data.audit.style_text }} flex items-start space-x-3 space-x-reverse">
            <i class="fa-solid fa-triangle-exclamation text-xl mt-0.5"></i>
            <div>
                <h4 class="font-bold text-sm uppercase tracking-wider">ביקורת איכות: {{ data.audit.status }}</h4>
                <p class="text-sm mt-0.5 text-slate-300">{{ data.audit.message }}</p>
            </div>
        </div>
        {% endif %}

        <!-- CARDS -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- SHOP FLOOR -->
            <div class="bg-slate-900 border-2 border-blue-500/50 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between shadow-2xl">
                <div class="absolute top-0 left-0 bg-blue-600 text-white text-[10px] font-black uppercase px-3 py-1 rounded-br-xl tracking-wider">
                    סטנדרט מומלץ לייצור
                </div>
                <div>
                    <div class="flex items-center space-x-2 space-x-reverse mb-2">
                        <i class="fa-solid fa-shield-halved text-blue-400"></i>
                        <h3 class="font-bold text-lg text-white">1. Shop Floor Spec</h3>
                    </div>
                    <p class="text-xs text-slate-400 mb-6">מקסימום סובלנות ויציבות בשימוש בסכין קבועה 23.80 מ"מ.</p>
                    <div class="space-y-4">
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                            <span class="text-xs text-slate-500 font-medium block">גובה סכין ביג בשטנץ</span>
                            <span class="text-xl font-black text-blue-400">{{ data.shop_floor.rule_height }}</span>
                            <span class="text-[10px] text-emerald-400 font-bold block mt-0.5">סכין קבועה סטנדרטית</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">עובי פלטה</span>
                                <span class="text-sm font-bold text-slate-200">1.00 mm Steel</span>
                            </div>
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">עומק ערוץ (D)</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.shop_floor.depth }}</span>
                            </div>
                        </div>
                        <div class="bg-slate-950/50 p-4 rounded-xl border border-slate-800 space-y-2">
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">עם הסיבים (Parallel):</span>
                                <span class="font-bold text-slate-100">{{ data.shop_floor.width_parallel }}</span>
                            </div>
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">נגד הסיבים (Cross-grain):</span>
                                <span class="font-bold text-slate-100">{{ data.shop_floor.width_cross }}</span>
                            </div>
                            <div class="pt-2 border-t border-slate-800 flex justify-between items-center text-xs">
                                <span class="text-blue-400 font-bold">רוחב מאוחד בטוח:</span>
                                <span class="font-black text-blue-300 text-sm">{{ data.shop_floor.width_unified }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-6 pt-4 border-t border-slate-800">
                    <p class="text-[11px] text-slate-400 leading-relaxed"><i class="fa-solid fa-circle-check text-emerald-400 ml-1"></i> בטוח מפני שינויי עובי קרטון. ללא צורך בשינוי גבהי סכין בעץ.</p>
                </div>
            </div>

            <!-- MARBACH SPEC -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
                <div>
                    <div class="flex items-center space-x-2 space-x-reverse mb-2">
                        <i class="fa-solid fa-bolt text-amber-400"></i>
                        <h3 class="font-bold text-lg text-white">2. Marbach Spec</h3>
                    </div>
                    <p class="text-xs text-slate-400 mb-6">עבודה במהירות גבוהה מדויקת עם סכינים מונמכות.</p>
                    <div class="space-y-4">
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                            <span class="text-xs text-slate-500 font-medium block">גובה סכין ביג בשטנץ</span>
                            <span class="text-xl font-black text-amber-400">{{ data.marbach.rule_height }}</span>
                            <span class="text-[10px] text-amber-400 font-bold block mt-0.5">דורש סכין מונמכת</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">עובי פלטה</span>
                                <span class="text-sm font-bold text-slate-200">1.00 mm Steel</span>
                            </div>
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">עומק ערוץ (D)</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.marbach.depth }}</span>
                            </div>
                        </div>
                        <div class="bg-slate-950/50 p-4 rounded-xl border border-slate-800 space-y-2">
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">עם הסיבים (Parallel):</span>
                                <span class="font-bold text-slate-100">{{ data.marbach.width_parallel }}</span>
                            </div>
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">נגד הסיבים (Cross-grain):</span>
                                <span class="font-bold text-slate-100">{{ data.marbach.width_cross }}</span>
                            </div>
                            <div class="pt-2 border-t border-slate-800 flex justify-between items-center text-xs">
                                <span class="text-amber-400 font-bold">רוחב מאוחד:</span>
                                <span class="font-black text-amber-300 text-sm">{{ data.marbach.width_unified }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-6 pt-4 border-t border-slate-800">
                    <p class="text-[11px] text-slate-400 leading-relaxed"><i class="fa-solid fa-circle-info text-amber-400 ml-1"></i> מפחית ויברציות במכונה מעל 9,000 גיליונות בשעה.</p>
                </div>
            </div>

            <!-- PERTINAX -->
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
                <div>
                    <div class="flex items-center space-x-2 space-x-reverse mb-2">
                        <i class="fa-solid fa-sheet-plastic text-purple-400"></i>
                        <h3 class="font-bold text-lg text-white">3. Pertinax Matrix</h3>
                    </div>
                    <p class="text-xs text-slate-400 mb-6">מטריצת פרטינקס מסורתית לפי נוסחת הפחתת סכין (23.80 - D).</p>
                    <div class="space-y-4">
                        <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                            <span class="text-xs text-slate-500 font-medium block">גובה סכין ביג בשטנץ</span>
                            <span class="text-xl font-black text-purple-400">{{ data.pertinax.rule_height }}</span>
                            <span class="text-[10px] text-purple-400 font-bold block mt-0.5">משתנה (23.80 - עומק)</span>
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">עובי פרטינקס</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.pertinax.plate_thickness }}</span>
                            </div>
                            <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
                                <span class="text-xs text-slate-500 font-medium block">עומק ערוץ (D)</span>
                                <span class="text-sm font-bold text-slate-200">{{ data.pertinax.depth }}</span>
                            </div>
                        </div>
                        <div class="bg-slate-950/50 p-4 rounded-xl border border-slate-800 space-y-2">
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">עם הסיבים (Parallel):</span>
                                <span class="font-bold text-slate-100">{{ data.pertinax.width_parallel }}</span>
                            </div>
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-slate-400">נגד הסיבים (Cross-grain):</span>
                                <span class="font-bold text-slate-100">{{ data.pertinax.width_cross }}</span>
                            </div>
                            <div class="pt-2 border-t border-slate-800 flex justify-between items-center text-xs">
                                <span class="text-purple-400 font-bold">רוחב מאוחד:</span>
                                <span class="font-black text-purple-300 text-sm">{{ data.pertinax.width_unified }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-6 pt-4 border-t border-slate-800">
                    <p class="text-[11px] text-slate-400 leading-relaxed"><i class="fa-solid fa-arrows-rotate text-purple-400 ml-1"></i> עובי הפרטינקס שווה לעובי הקרטון. יש להחליף סכינים בכל שינוי עובי.</p>
                </div>
            </div>
        </div>

    </main>

    <footer class="border-t border-slate-800 py-4 text-center text-xs text-slate-500">
        אומן לייזר - מבלטים וצילינדרים לנייר וקרטון • כלי חישוב פנימי לבית המלאכה
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
