#!/usr/bin/env python3
"""
Gemini Spark — Daily GoHighLevel Email Report Compiler
Compiles an inline-CSS, Gmail/Outlook/Apple Mail compatible HTML daily shortlist
specifically focused on GoHighLevel & CRM automation opportunities.
"""

import os
import sys
import json

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def generate_email_html(data_path, dashboard_url=None):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    meta = data.get("metadata", {})
    candidate = meta.get("candidate", {})
    kpis = meta.get("kpis", {})
    all_jobs = data.get("jobs", [])
    
    # Active jobs strictly 0-7 days
    active_jobs = [j for j in all_jobs if j.get("is_active", True)]
    top5 = active_jobs[:5]
    reports = meta.get("reports", {})

    live_dashboard_url = dashboard_url or "https://chrooniq.github.io/gemini-spark-job-dashboard/"
    excel_url = reports.get("excel_url", "#")
    drive_folder_url = reports.get("drive_folder_url", "#")
    portfolio_url = candidate.get("portfolio_url", "https://sohaibmahmood.vibepreview.com/")

    # Build Top 5 cards HTML
    top5_html_cards = []
    for job in top5:
        rank = job.get("rank", 1)
        score = job.get("score", 90)
        title = job.get("title", "")
        company = job.get("company", "")
        location = job.get("location", "")
        work_mode = job.get("work_mode", "100% Remote")
        salary = job.get("salary", "Competitive")
        exp_req = job.get("experience_req", "3+ years")
        cand_exp = job.get("candidate_exp", "4 years")
        priority = job.get("priority", "Priority 1 — Apply")
        freshness = job.get("freshness_badge", "FRESH")
        why = job.get("why_matches", "")
        matched_skills = ", ".join(job.get("matched_skills", []))
        missing_skills = ", ".join(job.get("missing_skills", []))
        concerns = job.get("concerns", "")
        app_url = job.get("app_url", "#")
        orig_url = job.get("original_url", "#")
        source = job.get("source", "Direct ATS")

        badge_color = "#16A34A" if score >= 90 else "#2563EB"
        badge_bg = "#DCFCE7" if score >= 90 else "#EFF6FF"
        card_border = "#10B981" if rank <= 3 else "#3B82F6"

        card_html = f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 18px; background-color: #FFFFFF; border: 1px solid #E5E7EB; border-left: 4px solid {card_border}; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden;">
          <tr>
            <td style="padding: 16px 18px;">
              <!-- Card Header -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td valign="top" style="text-align: left;">
                    <div style="font-size: 11px; font-weight: 700; color: #2563EB; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                      #{rank} Ranked GHL Fit &nbsp;•&nbsp; <span style="background-color: #FEF3C7; color: #92400E; padding: 2px 6px; border-radius: 4px; font-weight: 800;">{freshness}</span> &nbsp;•&nbsp; <span style="color: #6B7280;">{source}</span>
                    </div>
                    <h3 style="margin: 0 0 4px 0; font-size: 15px; font-weight: 700; color: #111827; line-height: 1.3;">
                      {title}
                    </h3>
                    <div style="font-size: 13px; font-weight: 600; color: #4B5563;">
                      🏢 {company} &nbsp;•&nbsp; 📍 {location} ({work_mode})
                    </div>
                  </td>
                  <td valign="top" align="right" style="width: 75px; text-align: right;">
                    <div style="display: inline-block; background-color: {badge_bg}; border: 1px solid {badge_color}; color: {badge_color}; padding: 4px 8px; border-radius: 6px; text-align: center;">
                      <div style="font-size: 15px; font-weight: 800; font-family: 'JetBrains Mono', monospace, Arial; line-height: 1;">{score}%</div>
                      <div style="font-size: 9px; font-weight: 700; text-transform: uppercase; margin-top: 2px;">MATCH</div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Meta pills -->
              <div style="margin: 10px 0 12px 0; padding: 6px 10px; background-color: #F9FAFB; border-radius: 6px; border: 1px solid #F3F4F6; font-size: 11px; color: #374151;">
                <span style="display: inline-block; margin-right: 10px;">💼 <b>Req:</b> {exp_req} (You: {cand_exp})</span>
                <span style="display: inline-block; margin-right: 10px;">💰 <b>Salary:</b> {salary}</span>
                <span style="display: inline-block; font-weight: 700; color: #991B1B;">{priority}</span>
              </div>

              <!-- Why it matches -->
              <div style="margin-bottom: 8px;">
                <div style="font-size: 10px; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">WHY THIS MATCHES</div>
                <p style="margin: 0; font-size: 12px; color: #1F2937; line-height: 1.4;">
                  {why}
                </p>
              </div>

              <!-- Skills info -->
              <div style="margin-bottom: 12px; font-size: 11px; line-height: 1.45;">
                <div style="margin-bottom: 3px;"><b style="color: #059669;">✓ Verified Skills:</b> <span style="color: #374151;">{matched_skills}</span></div>
                {f'<div style="margin-bottom: 3px;"><b style="color: #DC2626;">⚠ Missing / Bonus:</b> <span style="color: #374151;">{missing_skills}</span></div>' if missing_skills and "None" not in missing_skills else ''}
              </div>

              <!-- Action button -->
              <table border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="left">
                    <a href="{app_url}" target="_blank" style="display: inline-block; background-color: #2563EB; color: #FFFFFF; font-size: 11px; font-weight: 700; text-decoration: none; padding: 7px 16px; border-radius: 6px;">
                      Apply Directly →
                    </a>
                  </td>
                  <td align="left" style="padding-left: 8px;">
                    <a href="{orig_url}" target="_blank" style="display: inline-block; background-color: #F3F4F6; color: #374151; font-size: 11px; font-weight: 600; text-decoration: none; padding: 7px 12px; border-radius: 6px;">
                      View Listing
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
        """
        top5_html_cards.append(card_html)

    all_cards_html = "\n".join(top5_html_cards)

    # Email HTML structure
    html_email = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gemini Spark | GoHighLevel Job Intelligence</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F3F4F6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #111827; -webkit-font-smoothing: antialiased;">

  <!-- Outer container table -->
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F3F4F6; padding: 20px 10px;">
    <tr>
      <td align="center">
        <!-- Main Card Wrapper (Max 640px) -->
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 640px; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; border: 1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">

          <!-- Brand Header -->
          <tr>
            <td style="background-color: #0F172A; padding: 24px 20px; text-align: left;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <div style="font-size: 10px; font-weight: 800; color: #38BDF8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px;">
                      ⚡ GEMINI SPARK • AI JOB INTELLIGENCE
                    </div>
                    <h1 style="margin: 0 0 4px 0; font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">
                      GoHighLevel Daily Shortlist
                    </h1>
                    <p style="margin: 0; font-size: 12px; color: #94A3B8;">
                      Candidate: <b style="color: #F8FAFC;">{candidate.get('name', 'Sohaib Mahmood')}</b> &nbsp;•&nbsp; <b style="color: #34D399;">0–7 Days Fresh Only</b>
                    </p>
                  </td>
                  <td align="right" valign="top" style="width: 110px;">
                    <span style="display: inline-block; background-color: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4); color: #6EE7B7; font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 20px; text-transform: uppercase;">
                      ● LIVE 3H REFRESH
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Summary Introduction -->
          <tr>
            <td style="padding: 14px 20px; background-color: #F8FAFC; border-bottom: 1px solid #E5E7EB;">
              <p style="margin: 0; font-size: 12px; color: #475569; line-height: 1.4;">
                Strict GoHighLevel career feed for Sohaib Mahmood. All jobs filtered within 0–7 days max age and matched against your 4-year GHL & CRM automation portfolio.
              </p>
            </td>
          </tr>

          <!-- Daily Overview KPI Block -->
          <tr>
            <td style="padding: 16px 20px; border-bottom: 1px solid #E5E7EB;">
              <div style="font-size: 10px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">
                INTELLIGENCE OVERVIEW
              </div>
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="center" style="width: 25%; padding: 10px 4px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px 0 0 6px;">
                    <div style="font-size: 18px; font-weight: 800; color: #0F172A; font-family: 'JetBrains Mono', monospace, Arial;">{kpis.get('new_jobs_count', len(active_jobs))}</div>
                    <div style="font-size: 9px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-top: 2px;">New Jobs</div>
                  </td>
                  <td align="center" style="width: 25%; padding: 10px 4px; background-color: #F8FAFC; border-top: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0;">
                    <div style="font-size: 18px; font-weight: 800; color: #0F172A; font-family: 'JetBrains Mono', monospace, Arial;">{kpis.get('active_jobs_count', len(active_jobs))}</div>
                    <div style="font-size: 9px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-top: 2px;">Fresh (0–7D)</div>
                  </td>
                  <td align="center" style="width: 25%; padding: 10px 4px; background-color: #F8FAFC; border-top: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0;">
                    <div style="font-size: 18px; font-weight: 800; color: #2563EB; font-family: 'JetBrains Mono', monospace, Arial;">{kpis.get('top_5_count', 5)}</div>
                    <div style="font-size: 9px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-top: 2px;">Shortlist</div>
                  </td>
                  <td align="center" style="width: 25%; padding: 10px 4px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0 6px 6px 0;">
                    <div style="font-size: 18px; font-weight: 800; color: #16A34A; font-family: 'JetBrains Mono', monospace, Arial;">{kpis.get('top_match_score', 98)}%</div>
                    <div style="font-size: 9px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-top: 2px;">Top Match</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Primary CTA Banner -->
          <tr>
            <td style="padding: 14px 20px; background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); text-align: center;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="left" style="color: #FFFFFF;">
                    <div style="font-size: 13px; font-weight: 700;">Live Interactive GHL Dashboard</div>
                    <div style="font-size: 11px; color: #94A3B8;">Filter by Freshness, trigger manual scans, and track application status.</div>
                  </td>
                  <td align="right" style="width: 140px;">
                    <a href="{live_dashboard_url}" target="_blank" style="display: inline-block; background-color: #2563EB; color: #FFFFFF; font-size: 11px; font-weight: 700; text-decoration: none; padding: 8px 14px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                      Open Dashboard →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Top Opportunities Section -->
          <tr>
            <td style="padding: 20px;">
              <div style="font-size: 11px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px;">
                🎯 TOP GHL OPPORTUNITIES
              </div>

              <!-- Injected Job Cards -->
              {all_cards_html}

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0F172A; padding: 18px 20px; text-align: center; color: #94A3B8; font-size: 11px;">
              <div style="font-weight: 700; color: #F1F5F9; margin-bottom: 3px;">Gemini Spark • AI Career Intelligence</div>
              <div>Autonomous GoHighLevel job discovery & ranking for Sohaib Mahmood.</div>
              <div style="margin-top: 5px; color: #64748B;">Lahore, Pakistan (UTC+5) • 100% Worldwide Remote Career Hub</div>
            </td>
          </tr>

        </table>
        <!-- End Wrapper -->
      </td>
    </tr>
  </table>

</body>
</html>
"""
    return html_email

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "latest.json")
    output_file = os.path.join(base_dir, "email_template.html")
    
    if os.path.exists(data_path):
        html_output = generate_email_html(data_path)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_output)
        print(f"✓ Redesigned GHL email HTML template written to {output_file}")
    else:
        print(f"Error: {data_path} not found.")
