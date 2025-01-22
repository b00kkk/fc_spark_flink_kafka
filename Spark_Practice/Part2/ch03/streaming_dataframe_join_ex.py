from pyspark.sql import SparkSession
import pyspark.sql.functions as F

if __name__ == '__main__':
    ss: SparkSession = SparkSession.builder\
        .master("local[2]")\
        .appName("streaming dataframe join example")\
        .getOrCreate()

    authors = ss.read\
        .option("inferSchema", True).json("data/authors.json")

    books= ss.read \
        .option("inferSchema", True).json("data/books.json")

    # 1. join (static, static)
    authors_books_df = authors.join(books,
                                    authors["book_id"] == books["id"],
                                    "inner")
    # authors_books_df.show()

    # 2. join (static, stream)

    def join_stream_with_static():
        streamed_books = ss\
            .readStream\
            .format("socket")\
            .option("host","localhost")\
            .option("port",12345)\
            .load().select(F.from_json(F.col("value"),
                                       books.schema).alias("book"))\
            .selectExpr("book.id as id",
                        "book.name as name",
                        "book.year as year")

        # 잘 가져와 졌는지 확
        # streamed_books.writeStream\
        #     .format("console")\
        #     .outputMode("append")\
        #     .start()\
        #     .awaitTermination()

        authors_books_df = authors.join(streamed_books,
                                        authors["book_id"] == streamed_books["id"],
                                        "full_outer")
        # inner 후 left 실행해 봄
        # left outer join은 static 왼쪽 stream이 오른쪽일 때 지원이 안됨 그래서 right 실행
        # right outer join 일 때도 반대의 경우면 에러가 발생할 것
        # full_outer를 넣으면 제약조건에 의해 에러가 발생

        authors_books_df.writeStream\
            .format("console")\
            .outputMode("append")\
            .start()\
            .awaitTermination()
        # join 연산은 마이크로 배치가 만들어질 때 마다 사용됨


#join_stream_with_static()

# 3. join (stream, stream)
def join_stream_with_stream():
    streamed_books = \
        ss.readStream.format("socket") \
            .option("host", "localhost") \
            .option("port", 12345) \
            .load() \
            .select(F.from_json(F.col("value"),
                                books.schema).alias("book")) \
            .selectExpr("book.id as id",
                        "book.name as name",
                        "book.year as year")

    streamed_authors = \
        ss.readStream.format("socket") \
            .option("host", "localhost") \
            .option("port", 12346) \
            .load() \
            .select(F.from_json(F.col("value"),
                                authors.schema).alias("author")) \
            .selectExpr("author.id as id",
                        "author.name as name",
                        "author.book_id as book_id")

    # join : PER BATCH
    authors_books_df = \
        streamed_authors.join(streamed_books,
                              streamed_authors["book_id"] == streamed_books["id"],
                              "inner")

    authors_books_df.writeStream \
        .format("console") \
        .outputMode("append") \
        .start().awaitTermination()


join_stream_with_stream()
