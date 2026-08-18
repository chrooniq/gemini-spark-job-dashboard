import json
import os

def generate_email_html(data_path, dashboard_url=None):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    meta = data["metadata"]
    candidate = meta["candidate"]
    kpis = meta["kpis"]
    jobs = data["jobs"]
    top5 = jobs[:5]
    insights = data["market_insights"]
    reports = meta["reports"]

    live_dashboard_url = dashboard_url or "https://sohaibmahmood.github.io/gemini-spark-job-dashboard/"
    excel_url = reports.get("excel_url", "#")
    drive_folder_url = reports.get("drive_folder_url", "#")
    portfolio_url = candidate.get("portfolio_url", "https://sohaibmahmood.vibepreview.com/")

    # Build Top 5 cards HTML
    top5_html_cards = []
    for job in top5:
        rank = job["rank"]
        score = job["score"]
        title = job["title"]
        company = job["company"]
        location = job["location"]
        work_mode = job["work_mode"]
        salary = job["salary"]
        exp_req = job["experience_req"]
        cand_exp = job["candidate_exp"]
        priority = job["priority"]
        why = job["why_matches"]
        matched_skills = ", ".join(job["matched_skills"])
        missing_skills = ", ".join(job["missing_skills"])
        concerns = job["concerns"]
        app_url = job["app_url"]
        orig_url = job["original_url"]
        source = job["source"]

        badge_color = "#16A34A" if score >= 90 else "#2563EB"
        badge_bg = "#DCFCE7" if score >= 90 else "#EFF6FF"
        card_border = "#10B981" if rank <= 3 else "#3B82F6"

        card_html = f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 20px; background-color: #FFFFFF; border: 1px solid #E5E7EB; border-left: 4px solid {card_border}; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden;">
          <tr>
            <td style="padding: 18px 20px;">
              <!-- Card Header -->
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td valign="top" style="text-align: left;">
                    <div style="font-size: 11px; font-weight: 700; color: #2563EB; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
                      #{rank} Ranked Opportunity • <span style="color: #6B7280;">{source}</span>
                    </div>
                    <h3 style="margin: 0 0 6px 0; font-size: 16px; font-weight: 700; color: #111827; line-height: 1.3;">
                      {title}
                    </h3>
                    <div style="font-size: 13px; font-weight: 600; color: #4B5563;">
                      🏢 {company} &nbsp;•&nbsp; 📍 {location} ({work_mode})
                    </div>
                  </td>
                  <td valign="top" align="right" style="width: 80px; text-align: right;">
                    <div style="display: inline-block; background-color: {badge_bg}; border: 1px solid {badge_color}; color: {badge_color}; padding: 4px 8px; border-radius: 6px; text-align: center;">
                      <div style="font-size: 16px; font-weight: 800; font-family: 'JetBrains Mono', monospace, Arial; line-height: 1;">{score}%</div>
                      <div style="font-size: 9px; font-weight: 700; text-transform: uppercase; margin-top: 2px;">MATCH</div>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Meta pills -->
              <div style="margin: 12px 0 14px 0; padding: 8px 12px; background-color: #F9FAFB; border-radius: 6px; border: 1px solid #F3F4F6; font-size: 12px; color: #374151;">
                <span style="display: inline-block; margin-right: 12px;">💼 <b>Req:</b> {exp_req} (You: {cand_exp})</span>
                <span style="display: inline-block; margin-right: 12px;">💰 <b>Salary:</b> {salary}</span>
                <span style="display: inline-block; font-weight: 700; color: #991B1B;">{priority}</span>
              </div>

              <!-- Why it matches -->
              <div style="margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px;">WHY THIS MATCHES</div>
                <p style="margin: 0; font-size: 13px; color: #1F2937; line-height: 1.45;">
                  {why}
                </p>
              </div>

              <!-- Skills info -->
              <div style="margin-bottom: 14px; font-size: 12px; line-height: 1.5;">
                <div style="margin-bottom: 4px;"><b style="color: #059669;">✓ Strong Matching Skills:</b> <span style="color: #374151;">{matched_skills}</span></div>
                {f'<div style="margin-bottom: 4px;"><b style="color: #DC2626;">⚠ Missing / Unverified:</b> <span style="color: #374151;">{missing_skills}</span></div>' if missing_skills and missing_skills != "None identified in core scope" and missing_skills != "None for listed technical scope" and missing_skills != "None identified" else ''}
                <div><b style="color: #6B7280;">ℹ Potential Considerations:</b> <span style="color: #4B5563;">{concerns}</span></div>
              </div>

              <!-- Action button -->
              <table border="0" cellspacing="0" cellpadding="0" style="margin-top: 12px;">
                <tr>
                  <td align="left">
                    <a href="{app_url}" target="_blank" style="display: inline-block; background-color: #2563EB; color: #FFFFFF; font-size: 12px; font-weight: 700; text-decoration: none; padding: 8px 18px; border-radius: 6px; letter-spacing: 0.2px;">
                      Apply Directly →
                    </a>
                  </td>
                  <td align="left" style="padding-left: 10px;">
                    <a href="{orig_url}" target="_blank" style="display: inline-block; background-color: #F3F4F6; color: #374151; font-size: 12px; font-weight: 600; text-decoration: none; padding: 8px 14px; border-radius: 6px;">
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
  <title>Gemini Spark | Daily Job Intelligence</title>
</head>
<body style="margin: 0; padding: 0; background-color: #F3F4F6; font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #111827; -webkit-font-smoothing: antialiased;">

  <!-- Outer container table -->
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F3F4F6; padding: 24px 12px;">
    <tr>
      <td align="center">
        <!-- Main Card Wrapper (Max 640px) -->
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 640px; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; border: 1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">

          <!-- Brand Header -->
          <tr>
            <td style="background-color: #111827; padding: 28px 24px; text-align: left;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td>
                    <div style="font-size: 11px; font-weight: 800; color: #3B82F6; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px;">
                      GEMINI SPARK • AI CAREER INTELLIGENCE
                    </div>
                    <h1 style="margin: 0 0 6px 0; font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">
                      Daily Shortlist & Career Report
                    </h1>
                    <p style="margin: 0; font-size: 13px; color: #9CA3AF;">
                      Candidate: <b style="color: #F3F4F6;">{candidate['name']}</b> &nbsp;•&nbsp; Date: <b style="color: #F3F4F6;">{meta['search_date']}</b>
                    </p>
                  </td>
                  <td align="right" valign="top" style="width: 120px;">
                    <span style="display: inline-block; background-color: rgba(37, 99, 235, 0.2); border: 1px solid rgba(59, 130, 246, 0.4); color: #93C5FD; font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 20px; text-transform: uppercase;">
                      100% REMOTE
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Summary Introduction -->
          <tr>
            <td style="padding: 18px 24px; background-color: #F9FAFB; border-bottom: 1px solid #E5E7EB;">
              <p style="margin: 0; font-size: 13px; color: #4B5563; line-height: 1.5;">
                Your daily shortlist of the strongest opportunities matching your professional GoHighLevel, CRM automation, n8n, and web development profile.
              </p>
            </td>
          </tr>

          <!-- Daily Overview KPI Block -->
          <tr>
            <td style="padding: 20px 24px; border-bottom: 1px solid #E5E7EB;">
              <div style="font-size: 11px; font-weight: 800; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                DAILY OVERVIEW
              </div>
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="center" style="width: 25%; padding: 12px 6px; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px 0 0 8px;">
                    <div style="font-size: 20px; font-weight: 800; color: #111827; font-family: 'JetBrains Mono', monospace, Arial;">{kpis['total_discovered']}</div>
                    <div style="font-size: 10px; font-weight: 700; color: #6B7280; text-transform: uppercase; margin-top: 2px;">Discovered</div>
                  </td>
                  <td align="center" style="width: 25%; padding: 12px 6px; background-color: #F9FAFB; border-top: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB; border-right: 1px solid #E5E7EB;">
                    <div style="font-size: 20px; font-weight: 800; color: #111827; font-family: 'JetBrains Mono', monospace, Arial;">{kpis['relevant_qualified']}</div>
                    <div style="font-size: 10px; font-weight: 700; color: #6B7280; text-transform: uppercase; margin-top: 2px;">Qualified</div>
                  </td>
                  <td align="center" style="width: 25%; padding: 12px 6px; background-color: #F9FAFB; border-top: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB; border-right: 1px solid #E5E7EB;">
                    <div style="font-size: 20px; font-weight: 800; color: #2563EB; font-family: 'JetBrains Mono', monospace, Arial;">{kpis['top_5_count']}</div>
                    <div style="font-size: 10px; font-weight: 700; color: #6B7280; text-transform: uppercase; margin-top: 2px;">Top Shortlist</div>
                  </td>
                  <td align="center" style="width: 25%; padding: 12px 6px; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 0 8px 8px 0;">
                    <div style="font-size: 20px; font-weight: 800; color: #16A34A; font-family: 'JetBrains Mono', monospace, Arial;">{kpis['top_match_score']}%</div>
                    <div style="font-size: 10px; font-weight: 700; color: #6B7280; text-transform: uppercase; margin-top: 2px;">Highest Match</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Primary CTA Banner -->
          <tr>
            <td style="padding: 16px 24px; background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); text-align: center;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="left" style="color: #FFFFFF;">
                    <div style="font-size: 14px; font-weight: 700;">Live Interactive Job Match Dashboard</div>
                    <div style="font-size: 12px; color: #94A3B8;">Filter, sort, track application statuses, and inspect historical reports.</div>
                  </td>
                  <td align="right" style="width: 160px;">
                    <a href="{live_dashboard_url}" target="_blank" style="display: inline-block; background-color: #2563EB; color: #FFFFFF; font-size: 12px; font-weight: 700; text-decoration: none; padding: 10px 18px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                      Open Dashboard →
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Top 5 Opportunities Section -->
          <tr>
            <td style="padding: 24px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="font-size: 12px; font-weight: 800; color: #111827; text-transform: uppercase; letter-spacing: 0.5px;">
                  🎯 TOP 5 OPPORTUNITIES TODAY
                </div>
              </div>

              <!-- Injected Job Cards -->
              {all_cards_html}

            </td>
          </tr>

          <!-- Market Intelligence Box -->
          <tr>
            <td style="padding: 20px 24px; background-color: #F9FAFB; border-top: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB;">
              <div style="font-size: 11px; font-weight: 800; color: #111827; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                🧠 MARKET & CAREER INTELLIGENCE
              </div>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="font-size: 12px; line-height: 1.5; color: #374151;">
                <tr>
                  <td style="padding-bottom: 8px;">
                    <b style="color: #111827;">🔥 Most In-Demand Skills:</b> GoHighLevel SaaS Mode (71%), n8n Webhook Automation (50%), REST APIs (64%), OpenAI/Anthropic APIs (43%).
                  </td>
                </tr>
                <tr>
                  <td style="padding-bottom: 8px;">
                    <b style="color: #DC2626;">🧠 Biggest Skill Gap:</b> {insights['skill_gap_summary']['skill']} — {insights['skill_gap_summary']['market_demand']}
                  </td>
                </tr>
                <tr>
                  <td style="padding-bottom: 8px;">
                    <b style="color: #2563EB;">📈 Emerging Skills:</b> AI Agent / Tool-use connectors inside n8n, Model Context Protocol (MCP), and automated lead scoring.
                  </td>
                </tr>
                <tr>
                  <td>
                    <b style="color: #059669;">📄 Resume Insight:</b> Emphasize fault-tolerant webhook retry mechanisms and omni-channel messaging deliverability in your Core Skills.
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Reports & Artifacts Links -->
          <tr>
            <td style="padding: 20px 24px; text-align: center; background-color: #FFFFFF;">
              <div style="font-size: 12px; color: #6B7280; margin-bottom: 12px;">
                Your complete Top 25 job report and historical data are available:
              </div>
              <div>
                <a href="{excel_url}" target="_blank" style="display: inline-block; background-color: #F3F4F6; border: 1px solid #D1D5DB; color: #111827; font-size: 12px; font-weight: 600; text-decoration: none; padding: 7px 14px; border-radius: 6px; margin: 0 4px 6px;">
                  📊 Download Excel (.xlsx)
                </a>
                <a href="{live_dashboard_url}" target="_blank" style="display: inline-block; background-color: #2563EB; color: #FFFFFF; font-size: 12px; font-weight: 700; text-decoration: none; padding: 7px 14px; border-radius: 6px; margin: 0 4px 6px;">
                  🌐 Live Web Dashboard
                </a>
                <a href="{portfolio_url}" target="_blank" style="display: inline-block; background-color: #F3F4F6; border: 1px solid #D1D5DB; color: #111827; font-size: 12px; font-weight: 600; text-decoration: none; padding: 7px 14px; border-radius: 6px; margin: 0 4px 6px;">
                  💼 Portfolio (vibepreview)
                </a>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #111827; padding: 20px 24px; text-align: center; color: #9CA3AF; font-size: 11px;">
              <div style="font-weight: 700; color: #E5E7EB; margin-bottom: 4px;">Gemini Spark • AI Career Intelligence</div>
              <div>Daily automated job discovery and career analysis for Sohaib Mahmood.</div>
              <div style="margin-top: 6px; color: #6B7280;">Lahore, Pakistan (UTC+5) • 100% Worldwide Remote Career Hub</div>
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
    data_path = "/working_dir/c_f852dfa8ed7d66d6/gemini-spark-job-dashboard/data/latest.json"
    html_output = generate_email_html(data_path)
    output_file = "/working_dir/c_f852dfa8ed7d66d6/gemini-spark-job-dashboard/email_template.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"Redesigned email HTML template written to {output_file}")
