import PyPDF2

# Clean and re-run PDF generation after removing problematic unicode characters
def clean_text(text):
    return text.replace("–", "-").replace("’", "'").replace("•", "-").replace("•", "-")

pdf = PyPDF2()
pdf.set_auto_page_break(auto=True, margin=10)
pdf.add_page()

# Add content using cleaned text
pdf.chapter_title("Overview")
pdf.chapter_body(clean_text(
    "Goal: Boost fat loss and lean muscle with safe strength training and HIIT cardio.\n"
    "Total Duration: ~50 minutes\n"
    "Intensity Level: Moderate to High (adjust as needed)"
))

pdf.chapter_title("1. Warm-Up (8-10 minutes)")
pdf.chapter_body(clean_text(
    "- Treadmill walk: 3 min at 3.5-4 mph\n"
    "- Arm circles + shoulder rolls: 1 min\n"
    "- Bodyweight squats: 2 sets x 10 reps\n"
    "- Dynamic lunges: 1 min\n"
    "- Torso or standing twists: 1 min"
))

pdf.chapter_title("2. Strength Training (25 minutes)")
pdf.chapter_body(clean_text(
    "Lower Body:\n"
    "- Goblet Squats (light dumbbell): 3 sets x 10 reps\n"
    "- Leg Press Machine: 3 sets x 10-12 reps\n\n"
    "Upper Body:\n"
    "- Seated Row Machine or Dumbbell Rows: 3 sets x 10 reps\n"
    "- Incline Dumbbell Press or Chest Press Machine: 3 sets x 10 reps\n\n"
    "Core:\n"
    "- Plank: 3 x 30 seconds\n"
    "- Dead bug (on mat): 2 sets x 10 each side"
))

pdf.chapter_title("3. HIIT Cardio (12-15 minutes)")
pdf.chapter_body(clean_text(
    "Treadmill:\n"
    "- Warm-up: 2 min walk\n"
    "- 5 Rounds:\n  * 30 sec jog or fast walk (6-7 mph)\n  * 90 sec walk (3.5 mph)\n"
    "- Cool down: 2-3 min walk\n\n"
    "OR Elliptical:\n"
    "- 20 sec fast pace + 40 sec slow pace, repeat for 8-10 mins"
))

pdf.chapter_title("4. Cool Down & Stretching (5-7 minutes)")
pdf.chapter_body(clean_text(
    "- Slow walk/cycle: 2-3 min\n"
    "- Stretches (hold 20-30 sec each):\n"
    "  * Hamstring\n  * Quad\n  * Shoulder\n  * Neck\n  * Cobra pose"
))

pdf.chapter_title("Post-Workout Tips")
pdf.chapter_body(clean_text(
    "- Hydrate: Water + pinch of salt or coconut water\n"
    "- Snack/Meal within 45 min:\n"
    "  * Greek yogurt + banana\n"
    "  * Protein shake + almonds\n"
    "  * Grilled chicken + sweet potato"
))

# Save the cleaned PDF
pdf_path = "/mnt/data/Day3_Strength_HIIT_Workout.pdf"
pdf.output(pdf_path)
