import pandas as pd              # For reading and processing the CSV data
import matplotlib.pyplot as plt  # For plotting graphs
import matplotlib.dates as mdates  # For formatting x-axis dates in the original plot
import numpy as np               # For numeric operations (used implicitly via pandas)
from datetime import datetime    # For handling date parsing
from matplotlib.colors import to_rgba

color_palette = {
    "Warm Orange": "#f28d3c",
    "Golden Yellow": "#f3c03e",
    "Bright Cyan": "#04a6cc",
    "Vivid Magenta": "#d3288c",
    "Near Black": "#020101",
    "Rosy Pink": "#ed5186",
    "Burnt Orange": "#e75528",
    "Peach": "#f1915d",
    "Soft Apricot": "#faa954",
    "Deep Teal": "#0b4c65",
    "Electric Blue": "#0e5a85",
    "Steel Gray": "#7a7d85",
    "Ocean Teal": "#1f697e",
    "Midnight Blue": "#112d3f",
    "Frost White": "#f0f3f5",
    "Royal Blue": "#2e5e87",
    "Sky Blue": "#4fa0cb",
    "Indigo Shadow": "#1f344b",
    "Charcoal Gray": "#52545a",
    "Muted Cyan": "#7eb9cf",
    "Ash Gray": "#393b3f",
    "Chalk White": "#dce0e4"
}


def show_color():
    # Horizontal swatches
    fig, ax = plt.subplots(figsize=(len(color_palette) * 0.8, 2))

    for i, (name, hex_code) in enumerate(color_palette.items()):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=hex_code)) #type:ignore
        ax.text(i + 0.5, -0.1, name, ha='center', va='top', fontsize=8, rotation=45)

    ax.set_xlim(0, len(color_palette))
    ax.set_ylim(-0.5, 1)
    ax.axis("off")
    plt.title("Full Color Palette Preview", fontsize=14)
    plt.tight_layout()
    plt.show()

def bluecoats_season_trend():

    # Re-load and preprocess
    df = pd.read_csv("bluecoats_shows.csv")
    df['Show Date'] = pd.to_datetime(df['Show Date'])
    df['Year'] = df['Show Date'].dt.year
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

    # Filter: Keep seasons with >= 6 shows or most recent year
    year_counts = df['Year'].value_counts()
    latest_year = df['Year'].max()
    valid_years = year_counts[(year_counts >= 6) | (year_counts.index == latest_year)].index
    filtered_df = df[df['Year'].isin(valid_years)]

    # Convert dates to a fixed year (e.g. 2000) for aligned plotting
    filtered_df['Month-Day'] = filtered_df['Show Date'].apply(lambda d: datetime(2000, d.month, d.day))

    # Plotting
    plt.figure(figsize=(16, 8))
    years = sorted(filtered_df['Year'].unique())
    cmap = plt.cm.get_cmap('viridis', len(years))  # Use colormap for fading effect

    for idx, year in enumerate(years):
        year_df = filtered_df[filtered_df['Year'] == year].sort_values('Show Date')
        month_days = year_df['Month-Day']
        scores = year_df['Total']

        # # Fade older years
        # alpha = 1.0 - (len(years) - 1 - idx) * 0.06
        # alpha = max(alpha, 0.3)  # Prevent full fade-out

        # tempo - only 2025 
        if year == 2025:
            alpha = 1
        else: 
            alpha = 0.6 - (len(years) - 1 - idx) * 0.06
            alpha = max(alpha, 0.3)  # Prevent full fade-out

        # Plot line with fading color
        plt.plot(month_days, scores, label=f"{year}", marker='o', alpha=alpha, color=cmap(idx))

    # Annotate final placements beside the legend
    legend_labels = []
    for idx, year in enumerate(years):
        final_row = filtered_df[filtered_df['Year'] == year].sort_values('Show Date').iloc[-1]
        label = f"{year} ({final_row['Total_rank']}th)"
        legend_labels.append(label)

    # Format legend with adjusted placement
    plt.legend(legend_labels, title="Season (Final Placement)", loc='upper left', bbox_to_anchor=(1.01, 1))

    # Final chart formatting
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.title("Bluecoats Score Progression by Calendar Date (Overlapping Years)")
    plt.xlabel("Show Calendar Date")
    plt.ylabel("Total Score")
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)

    plt.show()

#bluecoats_season_trend()
def bluecoats_season_trend_highlight_drops():
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime

    color_palette = {
        2025: "#e75528",  # Bright Cyan
        2024: "#2e5e87",  # Royal Blue
        2023: "#f28d3c",  # Warm Orange
        2022: "#d3288c",  # Vivid Magenta
        2019: "#ed5186",  # Deep Teal
    }

    df = pd.read_csv("bluecoats_shows.csv")
    df['Show Date'] = pd.to_datetime(df['Show Date'])
    df['Year'] = df['Show Date'].dt.year
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

    # Filter years
    df = df[df['Year'].isin(color_palette.keys())]
    df['Month-Day'] = df['Show Date'].apply(lambda d: datetime(2000, d.month, d.day))

    plt.figure(figsize=(16, 8))
    for year in sorted(color_palette.keys()):
        year_df = df[df['Year'] == year].sort_values('Show Date')
        dates = list(year_df['Month-Day'])
        scores = list(year_df['Total'])
        color = color_palette[year]

        # Segment-wise plotting: faded for non-drops, bold for drops
        for i in range(1, len(scores)):
            x_segment = [dates[i - 1], dates[i]]
            y_segment = [scores[i - 1], scores[i]]
            drop = scores[i] < scores[i - 1]
            alpha = 1.0 if drop else 0.25
            linewidth = 3.5 if drop else 1.5
            z = 5 if drop else 2

            plt.plot(x_segment, y_segment, color=color, linewidth=linewidth, alpha=alpha, zorder=z)

            if drop:
                # drop_val = scores[i - 1] - scores[i]
                plt.scatter(dates[i], scores[i], color=color, marker='v', s=60, edgecolors='black', zorder=6)
                # plt.text(dates[i], scores[i] - 0.7, f"-{drop_val:.1f}", color=color, fontsize=9, ha='center', fontweight='bold', zorder=7)

        # Scatter all points with soft fill
        plt.scatter(dates, scores, color=color, s=30, alpha=0.5, zorder=3)
        # Label last point for season
        plt.text(dates[-1], scores[-1] + 0.3, str(year), color=color, fontsize=10, weight='bold', ha='left')

    # Final formatting
    plt.title("Bluecoats Score Progression Since 2019 (Faded Non-Drops, Highlighted Dips)", fontsize=14)
    plt.xlabel("Calendar Date")
    plt.ylabel("Total Score")
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

def bluecoats_season_trend_highlight_improvements():

    color_palette = {
        2025: "#e75528",  # Burnt Orange
        2024: "#2e5e87",  # Royal Blue
        2023: "#f28d3c",  # Warm Orange
        2022: "#d3288c",  # Vivid Magenta
        2019: "#ed5186",  # Rosy Pink
    }

    df = pd.read_csv("bluecoats_shows.csv")
    df['Show Date'] = pd.to_datetime(df['Show Date'])
    df['Year'] = df['Show Date'].dt.year
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    df['Month-Day'] = df['Show Date'].apply(lambda d: datetime(2000, d.month, d.day))

    # Filter to years in palette
    df = df[df['Year'].isin(color_palette.keys())]

    plt.figure(figsize=(16, 8))

    for year in sorted(color_palette.keys()):
        year_df = df[df['Year'] == year].sort_values('Show Date')
        dates = list(year_df['Month-Day'])
        scores = list(year_df['Total'])
        color = color_palette[year]

        for i in range(1, len(scores)):
            x_segment = [dates[i - 1], dates[i]]
            y_segment = [scores[i - 1], scores[i]]
            delta = scores[i] - scores[i - 1]

            if delta >= 1.5:
                plt.plot(x_segment, y_segment, color=color, linewidth=3.5, zorder=5)
                plt.scatter(dates[i], scores[i], color=color, s=60, edgecolors='black', zorder=6)
            else:
                plt.plot(x_segment, y_segment, color=color, linewidth=1.2, alpha=0.15, zorder=2)

        # Plot points and label year
        plt.scatter(dates, scores, color=color, s=30, alpha=0.6, zorder=3)
        plt.text(dates[-1], scores[-1] + 0.3, str(year), color=color, fontsize=10, weight='bold', ha='left')

    # Formatting
    plt.title("Bluecoats Score Surges (Δ ≥ 1.0 Only)", fontsize=14)
    plt.xlabel("Calendar Date")
    plt.ylabel("Total Score")
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

def bluecoats_champ_seasons_plot():

    color_palette = {
        2025: "#e75528",  # Burnt Orange
        2024: "#2e5e87",  # Royal Blue
        2016: "#f28d3c",  # Warm Orange
    }

    df = pd.read_csv("bluecoats_shows.csv")
    df['Show Date'] = pd.to_datetime(df['Show Date'])
    df['Year'] = df['Show Date'].dt.year
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    df['Month-Day'] = df['Show Date'].apply(lambda d: datetime(2000, d.month, d.day))

    # Filter selected years only
    selected_years = color_palette.keys()
    df = df[df['Year'].isin(selected_years)]

    # Plot setup
    plt.figure(figsize=(16, 8))

    for year in sorted(selected_years):
        year_df = df[df['Year'] == year].sort_values('Show Date')
        dates = list(year_df['Month-Day'])
        scores = list(year_df['Total'])
        color = color_palette[year]

        plt.plot(dates, scores, color=color, linewidth=2.5, label=f"{year}", zorder=2)
        plt.scatter(dates, scores, color=color, s=30, alpha=0.8, zorder=3)
        plt.text(dates[-1], scores[-1] + 0.3, str(year), color=color, fontsize=10, weight='bold', ha='left')

    # Final formatting
    plt.title("Bluecoats Score Progression: 2016 vs 2024 vs 2025", fontsize=14)
    plt.xlabel("Calendar Date")
    plt.ylabel("Total Score")
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(title="Season", loc='upper left')
    plt.tight_layout()
    plt.show()


def bluecoats_caption_score_trend():

    color_palette = {
        2025: "#e75528",
        2024: "#2e5e87",
        2016: "#f28d3c",
        "2019–2024 Avg": "#7a7d85",
    }

    # Load and prep data
    df = pd.read_csv("bluecoats_shows.csv")
    df['Show Date'] = pd.to_datetime(df['Show Date'])
    df['Year'] = df['Show Date'].dt.year
    df['Month-Day'] = df['Show Date'].apply(lambda d: datetime(2000, d.month, d.day))

    # Define categories and matching columns
    caption_sets = {
        "General Effect": ["GE Total", "General Effect - TOT"],
        "Visual": ["Visual Total", "Visual - TOT"],
        "Music": ["Music Total", "Music - TOT"]
    }

    for caption_title, col_options in caption_sets.items():
        # Pick the first matching column that exists in the data
        caption_col = next((col for col in col_options if col in df.columns), None)
        if caption_col is None:
            print(f"⚠️ Could not find caption column for '{caption_title}'")
            continue

        plt.figure(figsize=(16, 6))

        # Plot 2025, 2024, 2016
        for year in [2025, 2024, 2016]:
            sub = df[df['Year'] == year].sort_values('Show Date')
            sub[caption_col] = pd.to_numeric(sub[caption_col], errors='coerce')
            dates = sub['Month-Day']
            plt.plot(dates, sub[caption_col], label=str(year), color=color_palette[year], linewidth=2.5)
            plt.scatter(dates, sub[caption_col], color=color_palette[year], s=30, alpha=0.8)

        # Plot 2019–2024 Average
        avg_df = df[df['Year'].between(2019, 2024)][['Month-Day', caption_col]].copy()
        avg_df[caption_col] = pd.to_numeric(avg_df[caption_col], errors='coerce')
        avg_df['Month-Day-Str'] = avg_df['Month-Day'].dt.strftime('%m-%d')
        avg_grouped = avg_df.groupby('Month-Day-Str', as_index=False)[caption_col].mean()
        avg_grouped['Month-Day'] = pd.to_datetime('2000-' + avg_grouped['Month-Day-Str'], format='%Y-%m-%d')

        plt.plot(avg_grouped['Month-Day'], avg_grouped[caption_col],
                 label="2019–2024 Avg", color=color_palette["2019–2024 Avg"],
                 linestyle='--', linewidth=2.5)

        # Final styling
        plt.title(f"Bluecoats {caption_title} Caption Scores", fontsize=15)
        plt.xlabel("Calendar Date")
        plt.ylabel("Score")
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.legend(title="Season")
        plt.tight_layout()
        plt.show()



















def crossmen_season_trend():
    file_path = 'score_by_show&corp.csv'
    df = pd.read_csv(file_path)

    # Clean and filter the data for Crossmen in 2022
    df['Show Date'] = pd.to_datetime(df['Show Date'], errors='coerce')
    crossmen_2022 = df[(df['Corp Name'] == 'Crossmen') & (df['Show Date'].dt.year == 2022)].copy()

    # Sort by date for correct plotting
    crossmen_2022.sort_values('Show Date', inplace=True)

    # Create a dual-axis plot: Total Score on the left y-axis, sub-categories on the right y-axis
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot Total Score on primary y-axis
    ax1.plot(crossmen_2022['Show Date'], crossmen_2022['Total'], label='Total Score', color='tab:blue', marker='o')
    ax1.set_ylabel('Total Score', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create secondary y-axis for sub-categories
    ax2 = ax1.twinx()
    ax2.plot(crossmen_2022['Show Date'], crossmen_2022['General Effect - TOT'], label='General Effect', color='tab:orange', marker='o')
    ax2.plot(crossmen_2022['Show Date'], crossmen_2022['Visual - TOT'], label='Visual', color='tab:green', marker='o')
    ax2.plot(crossmen_2022['Show Date'], crossmen_2022['Music - TOT'], label='Music', color='tab:red', marker='o')
    ax2.set_ylabel('Sub-category Scores', color='tab:gray')
    ax2.tick_params(axis='y', labelcolor='tab:gray')

    # Title and formatting
    plt.title('Crossmen Scores Over Time (2022)')
    fig.autofmt_xdate()
    fig.tight_layout()

    # Combined legend
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    plt.grid(True)
    plt.show()
