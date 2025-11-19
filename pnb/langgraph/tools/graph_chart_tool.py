import platform
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import io
import boto3
import uuid
from typing import Dict, Any, List, Optional
from pnb import SETTINGS, LOGGER
import base64
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class GraphDetails(BaseModel):
    x_col: Optional[str] = Field(
        None, description="Column name for x-axis (required for line/bar)"
    )
    y_col: Optional[str] = Field(
        None, description="Column name for y-axis (required for line/bar)"
    )
    label_col: Optional[str] = Field(
        None, description="Column name for labels (required for pie)"
    )
    value_col: Optional[str] = Field(
        None, description="Column name for values (required for pie)"
    )
    title: Optional[str] = Field(None, description="Title of the graph")
    x_label: Optional[str] = Field(None, description="Label for x-axis")
    y_label: Optional[str] = Field(None, description="Label for y-axis")


s3_client = boto3.client(
    "s3",
    aws_access_key_id=SETTINGS.AWS_ACCESS_KEY,
    aws_secret_access_key=SETTINGS.AWS_SECRET_KEY,
)

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 12


async def upload_to_s3(
    base64_image: str, bucket: str, prefix: str = "charts/"
) -> Optional[str]:
    """
    Upload base64-encoded image to S3 and return the URL.

    Args:
        base64_image (str): Base64-encoded image
        bucket (str): S3 bucket name
        prefix (str, optional): S3 prefix. Defaults to "charts/".

    Returns:
        Optional[str]: URL of the uploaded image or None if upload fails
    """
    try:
        if base64_image.startswith("data:image/png;base64,"):
            base64_image = base64_image.split(",")[1]

        image_data = base64.b64decode(base64_image)
        file_key = f"{prefix}{uuid.uuid4()}.png"

        s3_client.put_object(
            Bucket=bucket,
            Key=file_key,
            Body=image_data,
            ContentType="image/png",
        )

        url = f"{SETTINGS.AWS_BUCKET_URL}/{file_key}"
        LOGGER.debug(f"Uploaded image to S3: {url}")
        return url
    except Exception as e:
        LOGGER.error(f"Failed to upload image to S3: {str(e)}")
        return None


async def generate_line_plot(
    data: List[Dict[str, Any]], graph_details: GraphDetails
) -> Optional[str]:
    """
    Generate a line plot for sales data using LLM-provided details.

    Args:
        data (List[Dict[str, Any]]): Sales data with key-value pairs
        graph_details (GraphDetails): LLM-provided details

    Returns:
        Optional[str]: Base64-encoded image of the plot or None if generation fails
    """
    try:
        df = pd.DataFrame(data)
        if not graph_details.x_col or not graph_details.y_col:
            raise ValueError("graph_details must include 'x_col' and 'y_col'")
        if (
            graph_details.x_col not in df.columns
            or graph_details.y_col not in df.columns
        ):
            raise ValueError(
                f"Columns {graph_details.x_col} or {graph_details.y_col} not found in data"
            )

        plt.figure()
        sns.lineplot(
            data=df, x=graph_details.x_col, y=graph_details.y_col, marker="o", color="b"
        )
        if graph_details.title:
            plt.title(graph_details.title, fontsize=16, pad=15)
        plt.xlabel(
            graph_details.x_label if graph_details.x_label else graph_details.x_col
        )
        plt.ylabel(
            graph_details.y_label if graph_details.y_label else graph_details.y_col
        )
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100)
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        return img_str
    except Exception as e:
        LOGGER.error(f"Failed to generate line plot: {str(e)}")
        return None


async def generate_bar_plot(
    data: List[Dict[str, Any]], graph_details: GraphDetails
) -> Optional[str]:
    """
    Generate a bar plot for sales data using LLM-provided details.

    Args:
        data (List[Dict[str, Any]]): Sales data with key-value pairs
        graph_details (GraphDetails): LLM-provided details

    Returns:
        Optional[str]: Base64-encoded image of the plot or None if generation fails
    """
    try:
        df = pd.DataFrame(data)
        if not graph_details.x_col or not graph_details.y_col:
            raise ValueError("graph_details must include 'x_col' and 'y_col'")
        if (
            graph_details.x_col not in df.columns
            or graph_details.y_col not in df.columns
        ):
            raise ValueError(
                f"Columns {graph_details.x_col} or {graph_details.y_col} not found in data"
            )

        plt.figure()
        sns.barplot(
            data=df, x=graph_details.x_col, y=graph_details.y_col, palette="Blues_d"
        )
        if graph_details.title:
            plt.title(graph_details.title, fontsize=16, pad=15)
        plt.xlabel(
            graph_details.x_label if graph_details.x_label else graph_details.x_col
        )
        plt.ylabel(
            graph_details.y_label if graph_details.y_label else graph_details.y_col
        )
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100)
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        return img_str
    except Exception as e:
        LOGGER.error(f"Failed to generate bar plot: {str(e)}")
        return None


async def generate_pie_chart(
    data: List[Dict[str, Any]], graph_details: GraphDetails
) -> Optional[str]:
    """
    Generate a pie chart for sales data using LLM-provided details.

    Args:
        data (List[Dict[str, Any]]): Sales data with key-value pairs
        graph_details (GraphDetails): LLM-provided details

    Returns:
        Optional[str]: Base64-encoded image of the plot or None if generation fails
    """
    try:
        df = pd.DataFrame(data)
        if not graph_details.label_col or not graph_details.value_col:
            raise ValueError("graph_details must include 'label_col' and 'value_col'")
        if (
            graph_details.label_col not in df.columns
            or graph_details.value_col not in df.columns
        ):
            raise ValueError(
                f"Columns {graph_details.label_col} or {graph_details.value_col} not found in data"
            )

        plt.figure()
        plt.pie(
            df[graph_details.value_col],
            labels=df[graph_details.label_col],
            autopct="%1.1f%%",
            colors=sns.color_palette("Pastel1"),
        )
        if graph_details.title:
            plt.title(graph_details.title, fontsize=16, pad=15)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100)
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        return img_str
    except Exception as e:
        LOGGER.error(f"Failed to generate pie chart: {str(e)}")
        return None


@tool
async def handle_chart(
    data: List[Dict[str, Any]], chart_type: str, graph_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Tool to handle chart generation for a sales agent, uploading the chart to S3.

    Args:
        data (List[Dict[str, Any]]): Sales data as list of dictionaries. Each dictionary should contain key-value pairs
            representing data points (e.g., {'month': 'Jan', 'sales': 100, 'region': 'North'}).
        chart_type (str): Type of chart ('line', 'bar', 'pie').
        graph_details (Dict[str, Any]): LLM-provided details for chart customization. Must include specific keys based on
            chart_type:
            - For 'line' or 'bar': 'x_col' (str), 'y_col' (str), optional 'title', 'x_label', 'y_label'.
            - For 'pie': 'label_col' (str), 'value_col' (str), optional 'title'.

    Returns:
        Dict[str, Any]: Result with success status, message, and S3 URL of the chart.

    Examples:
        # Example 1: Line chart for monthly sales
        data = [
            {'month': 'Jan', 'sales': 100},
            {'month': 'Feb', 'sales': 150},
            {'month': 'Mar', 'sales': 200}
        ]
        chart_type = "line"
        graph_details = {
            "x_col": "month",
            "y_col": "sales",
            "title": "Monthly Sales Trend",
            "x_label": "Month",
            "y_label": "Sales ($)"
        }

        # Example 2: Bar chart for sales by region
        data = [
            {'region': 'North', 'sales': 500},
            {'region': 'South', 'sales': 300},
            {'region': 'West', 'sales': 400}
        ]
        chart_type = "bar"
        graph_details = {
            "x_col": "region",
            "y_col": "sales",
            "title": "Sales by Region",
            "x_label": "Region",
            "y_label": "Sales ($)"
        }

        # Example 3: Pie chart for sales distribution by product
        data = [
            {'product': 'Product A', 'sales': 40},
            {'product': 'Product B', 'sales': 30},
            {'product': 'Product C', 'sales': 20}
        ]
        chart_type = "pie"
        graph_details = {
            "label_col": "product",
            "value_col": "sales",
            "title": "Sales Distribution by Product"
        }
    """
    try:
        if not data:
            raise ValueError("Data cannot be empty")

        # Convert dict to GraphDetails, allowing partial input
        try:
            graph_details = GraphDetails(**graph_details)
        except Exception as e:
            LOGGER.error(f"Invalid graph_details format: {str(e)}")
            raise ValueError(f"Invalid graph_details format: {str(e)}")

        chart_functions = {
            "line": generate_line_plot,
            "bar": generate_bar_plot,
            "pie": generate_pie_chart,
        }

        if chart_type not in chart_functions:
            raise ValueError(
                f"Invalid chart type: {chart_type}. Supported types: {list(chart_functions.keys())}"
            )

        base64_image = await chart_functions[chart_type](data, graph_details)
        if not base64_image:
            raise ValueError(f"Failed to generate {chart_type} chart")

        chart_url = await upload_to_s3(base64_image, SETTINGS.AWS_BUCKET)
        if not chart_url:
            raise ValueError("Failed to upload chart to S3")

        return {
            "status": "success",
            "message": f"{chart_type.capitalize()} chart generated and uploaded successfully",
            "data": chart_url,
        }
    except Exception as e:
        LOGGER.error(f"Chart generation/upload error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate/upload chart: {str(e)}",
        }
